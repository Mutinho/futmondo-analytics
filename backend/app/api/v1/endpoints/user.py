"""User endpoints — current user info and championships config."""

import json
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional

router = APIRouter()


class ChampionshipConfig(BaseModel):
    championship_id: str
    name: str
    initial_budget: int = 200000000
    has_clauses: bool = False
    excluded_teams: List[str] = []


@router.get("/me")
async def get_current_user_info(request: Request) -> Dict:
    """Get info of the currently authenticated user."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    from app.services.db_connection import get_db
    db = get_db()
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        sql = "SELECT id, futmondo_email, futmondo_user_id, display_name, created_at, last_login FROM app_users WHERE id = ?"
        sql = db.adapt_params(sql)
        cursor.execute(sql, (user["user_id"],))
        row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "user": {
            "id": row[0],
            "email": row[1],
            "futmondo_user_id": row[2],
            "display_name": row[3],
            "created_at": str(row[4]) if row[4] else None,
            "last_login": str(row[5]) if row[5] else None,
        }
    }


@router.get("/championships")
async def get_user_championships(request: Request) -> Dict:
    """Get championships configured by the current user."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    from app.services.db_connection import get_db
    db = get_db()
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        sql = """
            SELECT championship_id, name, initial_budget, has_clauses, excluded_teams
            FROM user_championships WHERE user_id = ?
            ORDER BY name
        """
        sql = db.adapt_params(sql)
        cursor.execute(sql, (user["user_id"],))
        rows = cursor.fetchall()
    
    championships = []
    for row in rows:
        championships.append({
            "championship_id": row[0],
            "name": row[1],
            "initial_budget": row[2],
            "has_clauses": bool(row[3]),
            "excluded_teams": json.loads(row[4]) if row[4] else [],
        })
    
    return {"success": True, "championships": championships}


@router.post("/championships")
async def add_user_championship(request: Request, config: ChampionshipConfig) -> Dict:
    """Add or update a championship for the current user."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    from app.services.db_connection import get_db
    db = get_db()
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        excluded_json = json.dumps(config.excluded_teams)
        
        if db.db_type in ["postgresql", "postgres"]:
            cursor.execute("""
                INSERT INTO user_championships (user_id, championship_id, name, initial_budget, has_clauses, excluded_teams)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, championship_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    initial_budget = EXCLUDED.initial_budget,
                    has_clauses = EXCLUDED.has_clauses,
                    excluded_teams = EXCLUDED.excluded_teams
            """, (user["user_id"], config.championship_id, config.name, config.initial_budget, config.has_clauses, excluded_json))
        else:
            cursor.execute("""
                INSERT OR REPLACE INTO user_championships (user_id, championship_id, name, initial_budget, has_clauses, excluded_teams)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user["user_id"], config.championship_id, config.name, config.initial_budget, config.has_clauses, excluded_json))
    
    return {"success": True, "message": f"Championship '{config.name}' saved"}


@router.delete("/championships/{championship_id}")
async def delete_user_championship(request: Request, championship_id: str) -> Dict:
    """Remove a championship from the current user."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    from app.services.db_connection import get_db
    db = get_db()
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        sql = "DELETE FROM user_championships WHERE user_id = ? AND championship_id = ?"
        sql = db.adapt_params(sql)
        cursor.execute(sql, (user["user_id"], championship_id))
    
    return {"success": True, "message": "Championship removed"}
