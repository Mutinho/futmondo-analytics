"""Shared helpers for API endpoints."""

import json
from typing import Optional
from fastapi import Request, HTTPException
from app.services.futmondo_client import FutmondoClient


def get_championship_config(championship_id: str, request: Request) -> dict:
    """Get championship config from user_championships table.
    
    Falls back to default values if not found.
    
    Returns:
        dict with initial_budget, excluded_teams, has_clauses
    """
    from app.services.db_connection import get_db
    
    DEFAULTS = {"initial_budget": 200_000_000, "excluded_teams": set(), "has_clauses": False}
    
    user = getattr(request.state, "user", None)
    if not user:
        return DEFAULTS
    
    db = get_db()
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        sql = "SELECT initial_budget, excluded_teams, has_clauses FROM user_championships WHERE user_id = ? AND championship_id = ?"
        sql = db.adapt_params(sql)
        cursor.execute(sql, (user["user_id"], championship_id))
        row = cursor.fetchone()
    
    if row:
        return {
            "initial_budget": row[0] or 200_000_000,
            "excluded_teams": set(json.loads(row[1])) if row[1] else set(),
            "has_clauses": bool(row[2]),
        }
    
    return DEFAULTS


def get_user_futmondo_client(request: Request) -> FutmondoClient:
    """Get an authenticated FutmondoClient for the current user.
    
    Uses the session store (populated at login). If session lost (e.g. after restart),
    attempts to re-create it using the stored credentials in the session.
    
    Raises:
        HTTPException 401 if no session available and can't re-create
    """
    from app.auth.session_store import get_session_store
    
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    store = get_session_store()
    client = store.get_client(user["user_id"])
    
    if client:
        return client
    
    # Session lost (server restart). Try to re-create from stored credentials.
    # The session store keeps email+password in memory, but after restart they're gone.
    # Return 403 (not 401) so the interceptor doesn't try to refresh — goes straight to logout.
    raise HTTPException(
        status_code=403,
        detail="Sesión de Futmondo expirada. Por favor, inicia sesión de nuevo."
    )
