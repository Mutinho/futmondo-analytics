"""Assistant AI endpoint — chat with Gemini + conversation persistence."""

import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from app.services.assistant_service import get_assistant_service
from app.services.db_connection import get_db

router = APIRouter()


# --- Ensure conversations table exists ---
def _ensure_conversations_table():
    db = get_db()
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assistant_conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                championship_id TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT 'Nueva conversación',
                messages TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.commit()


try:
    _ensure_conversations_table()
except Exception:
    pass  # Will be created on first use


# --- Models ---

class ChatMessage(BaseModel):
    role: str
    content: str


class AskRequest(BaseModel):
    message: str
    championship_id: str
    conversation_id: Optional[str] = None
    history: Optional[List[ChatMessage]] = []


class AskResponse(BaseModel):
    response: str
    context_used: List[str]
    conversation_id: str


class ConversationSummary(BaseModel):
    id: str
    title: str
    championship_id: str
    updated_at: str
    message_count: int


class ConversationDetail(BaseModel):
    id: str
    title: str
    championship_id: str
    messages: List[ChatMessage]
    created_at: str
    updated_at: str


# --- Endpoints ---

@router.post("/ask", response_model=AskResponse)
async def ask_assistant(request: Request, body: AskRequest):
    """Send a question to the AI assistant. Auto-saves to conversation."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    service = get_assistant_service()
    user_id = user.get("user_id", "")
    now = datetime.now().isoformat()

    # Load or create conversation
    conversation_id = body.conversation_id
    db = get_db()

    if conversation_id:
        # Verify ownership
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(db.adapt_params(
                "SELECT messages FROM assistant_conversations WHERE id = ? AND user_id = ?"
            ), (conversation_id, user_id))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Conversación no encontrada")
            existing_messages = json.loads(row[0]) if row[0] else []
    else:
        # Create new conversation
        conversation_id = str(uuid.uuid4())
        title = body.message[:50] + ("..." if len(body.message) > 50 else "")
        existing_messages = []
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(db.adapt_params(
                "INSERT INTO assistant_conversations (id, user_id, championship_id, title, messages, created_at, updated_at) VALUES (?, ?, ?, ?, '[]', ?, ?)"
            ), (conversation_id, user_id, body.championship_id, title, now, now))
            conn.commit()

    # Use stored messages as history (override frontend history)
    history = [{"role": m["role"], "content": m["content"]} for m in existing_messages[-4:]]

    # Call the assistant
    result = await service.ask(
        user_id=user_id,
        championship_id=body.championship_id,
        message=body.message,
        history=history,
        request=request,
    )

    # Append both messages to conversation
    existing_messages.append({"role": "user", "content": body.message})
    existing_messages.append({"role": "assistant", "content": result["response"]})

    # Save to DB
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        cursor.execute(db.adapt_params(
            "UPDATE assistant_conversations SET messages = ?, updated_at = ? WHERE id = ?"
        ), (json.dumps(existing_messages, ensure_ascii=False), now, conversation_id))
        conn.commit()

    return AskResponse(
        response=result["response"],
        context_used=result["context_used"],
        conversation_id=conversation_id,
    )


@router.post("/ask/stream")
async def ask_assistant_stream(request: Request, body: AskRequest):
    """Send a question to the AI assistant with streaming response (SSE)."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    service = get_assistant_service()
    user_id = user.get("user_id", "")
    now = datetime.now().isoformat()

    # Load or create conversation
    conversation_id = body.conversation_id
    db = get_db()

    if conversation_id:
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(db.adapt_params(
                "SELECT messages FROM assistant_conversations WHERE id = ? AND user_id = ?"
            ), (conversation_id, user_id))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Conversación no encontrada")
            existing_messages = json.loads(row[0]) if row[0] else []
    else:
        conversation_id = str(uuid.uuid4())
        title = body.message[:50] + ("..." if len(body.message) > 50 else "")
        existing_messages = []
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(db.adapt_params(
                "INSERT INTO assistant_conversations (id, user_id, championship_id, title, messages, created_at, updated_at) VALUES (?, ?, ?, ?, '[]', ?, ?)"
            ), (conversation_id, user_id, body.championship_id, title, now, now))
            conn.commit()

    history = [{"role": m["role"], "content": m["content"]} for m in existing_messages[-4:]]

    async def event_generator():
        """Generate SSE events from the streaming response."""
        # Send conversation_id first
        yield f"data: {json.dumps({'type': 'start', 'conversation_id': conversation_id})}\n\n"

        full_response = ""
        context_used = []

        async for event in service.ask_stream(
            user_id=user_id,
            championship_id=body.championship_id,
            message=body.message,
            history=history,
            request=request,
        ):
            if event["type"] == "chunk":
                full_response += event["content"]
                yield f"data: {json.dumps({'type': 'chunk', 'content': event['content']})}\n\n"
            elif event["type"] == "done":
                context_used = event.get("context_used", [])
                if event.get("full_response"):
                    full_response = event["full_response"]

        # Save conversation to DB
        existing_messages.append({"role": "user", "content": body.message})
        existing_messages.append({"role": "assistant", "content": full_response})

        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(db.adapt_params(
                "UPDATE assistant_conversations SET messages = ?, updated_at = ? WHERE id = ?"
            ), (json.dumps(existing_messages, ensure_ascii=False), now, conversation_id))
            conn.commit()

        yield f"data: {json.dumps({'type': 'done', 'context_used': context_used})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/conversations")
async def list_conversations(request: Request, championship_id: Optional[str] = None):
    """List all conversations for the current user."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = user.get("user_id", "")
    db = get_db()

    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        if championship_id:
            cursor.execute(db.adapt_params(
                "SELECT id, title, championship_id, messages, updated_at FROM assistant_conversations WHERE user_id = ? AND championship_id = ? ORDER BY updated_at DESC"
            ), (user_id, championship_id))
        else:
            cursor.execute(db.adapt_params(
                "SELECT id, title, championship_id, messages, updated_at FROM assistant_conversations WHERE user_id = ? ORDER BY updated_at DESC"
            ), (user_id,))
        rows = cursor.fetchall()

    conversations = []
    for row in rows:
        messages = json.loads(row[3]) if row[3] else []
        conversations.append({
            "id": row[0],
            "title": row[1],
            "championship_id": row[2],
            "updated_at": row[4],
            "message_count": len(messages),
        })

    return {"conversations": conversations}


@router.get("/conversations/{conversation_id}")
async def get_conversation(request: Request, conversation_id: str):
    """Get a specific conversation with all messages."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = user.get("user_id", "")
    db = get_db()

    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        cursor.execute(db.adapt_params(
            "SELECT id, title, championship_id, messages, created_at, updated_at FROM assistant_conversations WHERE id = ? AND user_id = ?"
        ), (conversation_id, user_id))
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    messages = json.loads(row[3]) if row[3] else []
    return {
        "id": row[0],
        "title": row[1],
        "championship_id": row[2],
        "messages": messages,
        "created_at": row[4],
        "updated_at": row[5],
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(request: Request, conversation_id: str):
    """Delete a conversation."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = user.get("user_id", "")
    db = get_db()

    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        cursor.execute(db.adapt_params(
            "DELETE FROM assistant_conversations WHERE id = ? AND user_id = ?"
        ), (conversation_id, user_id))
        conn.commit()

    return {"success": True}


@router.put("/conversations/{conversation_id}/title")
async def update_conversation_title(request: Request, conversation_id: str, body: dict):
    """Update conversation title."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = user.get("user_id", "")
    title = body.get("title", "")
    if not title:
        raise HTTPException(status_code=400, detail="Title required")

    db = get_db()
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        cursor.execute(db.adapt_params(
            "UPDATE assistant_conversations SET title = ? WHERE id = ? AND user_id = ?"
        ), (title, conversation_id, user_id))
        conn.commit()

    return {"success": True}


@router.get("/usage")
async def get_usage(request: Request):
    """Get current assistant usage stats."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    service = get_assistant_service()
    return service.usage_tracker.get_usage_summary()
