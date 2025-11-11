"""
Simple authentication endpoints for UI access control.
"""

from datetime import datetime, timedelta
import secrets
from typing import Dict

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    role: str
    token: str
    expires_at: datetime


class SessionResponse(BaseModel):
    username: str
    role: str
    expires_at: datetime


USER_STORE: Dict[str, Dict[str, str]] = {
    "patxo": {"password": "aporlavictoria2026.", "role": "premium"},
}

TOKEN_TTL = timedelta(hours=12)
_TOKENS: Dict[str, Dict[str, datetime]] = {}


def _normalize_username(username: str) -> str:
    return username.strip().lower()


def _cleanup_tokens() -> None:
    now = datetime.utcnow()
    expired_tokens = [
        token for token, payload in _TOKENS.items() if payload["expires_at"] <= now
    ]
    for token in expired_tokens:
        _TOKENS.pop(token, None)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    """Authenticate user with static credentials."""
    _cleanup_tokens()

    username = _normalize_username(payload.username)
    record = USER_STORE.get(username)
    if not record or payload.password != record["password"]:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + TOKEN_TTL
    _TOKENS[token] = {
        "username": username,
        "role": record["role"],
        "expires_at": expires_at,
    }

    return LoginResponse(
        username=username,
        role=record["role"],
        token=token,
        expires_at=expires_at,
    )


@router.get("/session", response_model=SessionResponse)
def session(token: str = Query(..., description="Session token to validate")) -> SessionResponse:
    """Validate an existing session token."""
    _cleanup_tokens()

    session_info = _TOKENS.get(token)
    if not session_info:
        raise HTTPException(status_code=401, detail="Sesión no válida o expirada")

    if session_info["expires_at"] <= datetime.utcnow():
        _TOKENS.pop(token, None)
        raise HTTPException(status_code=401, detail="Sesión expirada")

    return SessionResponse(
        username=session_info["username"],
        role=session_info["role"],
        expires_at=session_info["expires_at"],
    )


@router.post("/logout")
def logout(token: str = Query(..., description="Session token to revoke")) -> Dict[str, str]:
    """Invalidate an existing session token."""
    removed = _TOKENS.pop(token, None)
    if not removed:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return {"status": "ok"}

