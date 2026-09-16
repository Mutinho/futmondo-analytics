"""Shared helpers for API endpoints."""

import json
from typing import Optional
from fastapi import Request, HTTPException
from app.services.futmondo_client import FutmondoClient


def clean_float(val, default=None):
    """Clean NaN/None/invalid values to float or default.
    
    Used across multiple endpoints to handle Futmondo API's inconsistent number fields.
    """
    if val is None or val == "NaN" or val == "":
        return default
    try:
        result = float(val)
        return default if result != result else result  # NaN check
    except (ValueError, TypeError):
        return default


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

    Resolves the session through ``SessionService.ensure_session``: it first
    tries the in-memory cache and, on a miss (e.g. after a server restart),
    rebuilds the session from the durable store and the encrypted re-auth handle
    (u1-durable-session). This replaces the previous behavior where a cold cache
    after a restart returned an opaque 403.

    Raises:
        HTTPException 401 if the user is not authenticated, if the session is
            unrecoverable (a fresh Futmondo login is required — actionable), or
            if re-authentication fails transiently (the client may retry).
    """
    from app.services.session_service import (
        SessionUnrecoverableError,
        TransientSessionError,
        get_session_service,
    )

    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    service = get_session_service()
    try:
        return service.ensure_session(user["user_id"])
    except SessionUnrecoverableError:
        # Session cannot be rebuilt (no durable credential, invalid credential,
        # or restart without protection). Actionable 401 so the client re-logs in
        # instead of hitting an opaque 403.
        raise HTTPException(
            status_code=401,
            detail="Tu sesión de Futmondo ha caducado. Vuelve a iniciar sesión para continuar.",
        )
    except TransientSessionError:
        # Recoverable upstream failure: do not force a re-login; ask to retry.
        raise HTTPException(
            status_code=401,
            detail="No se pudo restablecer la sesión de Futmondo temporalmente. Inténtalo de nuevo en unos segundos.",
        )
