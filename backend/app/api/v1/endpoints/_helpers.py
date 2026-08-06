"""Shared helpers for API endpoints."""

import json
from typing import Optional
from fastapi import Request


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
