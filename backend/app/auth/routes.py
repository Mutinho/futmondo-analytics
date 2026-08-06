"""
Auth endpoints — login, refresh, logout.
"""

import uuid
import logging
from fastapi import APIRouter, HTTPException, Request, status

from app.auth.models import LoginRequest, TokenResponse, RefreshRequest, RefreshResponse
from app.auth.jwt_utils import (
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.auth.token_store import (
    save_refresh_token,
    is_refresh_token_valid,
    revoke_refresh_token,
    revoke_all_user_tokens,
    upsert_user,
    get_user_by_email,
)
from app.services.futmondo_client import FutmondoClient
from app.core.config import BASE_URL

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    """Authenticate with Futmondo credentials and get JWT tokens."""
    
    # Validate credentials against Futmondo API
    client = FutmondoClient(body.email, body.password)
    login_ok = client.login()
    
    if not login_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas. Verifica tu email y contraseña de Futmondo.",
        )
    
    # Get or create our internal user
    existing_user = get_user_by_email(body.email)
    if existing_user:
        user_id = existing_user["id"]
    else:
        user_id = uuid.uuid4().hex
    
    # Upsert user record
    display_name = body.email.split("@")[0]
    upsert_user(
        user_id=user_id,
        email=body.email,
        futmondo_user_id=client.user_id or "",
        display_name=display_name,
    )
    
    # Generate tokens
    access_token = create_access_token(
        user_id=user_id,
        email=body.email,
        futmondo_user_id=client.user_id or "",
    )
    
    refresh_token, token_hash, expires_at = create_refresh_token(user_id)
    save_refresh_token(token_hash, user_id, expires_at)
    
    logger.info(f"✅ User logged in: {body.email} (id={user_id})")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user_id,
        email=body.email,
        display_name=display_name,
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(body: RefreshRequest):
    """Get a new access token using a refresh token."""
    
    # Verify the refresh token signature
    payload = verify_token(body.refresh_token, expected_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
        )
    
    # Check if token is revoked
    token_hash = hash_token(body.refresh_token)
    if not is_refresh_token_valid(token_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revocado",
        )
    
    user_id = payload["sub"]
    
    # Get user info for the new access token
    from app.auth.token_store import get_user_by_email
    # We need email from somewhere — look up by user_id
    db = __import__('app.services.db_connection', fromlist=['get_db']).get_db()
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        sql = "SELECT futmondo_email, futmondo_user_id FROM app_users WHERE id = ?"
        sql = db.adapt_params(sql)
        cursor.execute(sql, (user_id,))
        row = cursor.fetchone()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    
    email, futmondo_uid = row[0], row[1] or ""
    
    # Issue new access token
    access_token = create_access_token(
        user_id=user_id,
        email=email,
        futmondo_user_id=futmondo_uid,
    )
    
    return RefreshResponse(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout")
async def logout(body: RefreshRequest):
    """Revoke the refresh token (logout)."""
    
    token_hash = hash_token(body.refresh_token)
    revoke_refresh_token(token_hash)
    
    logger.info("User logged out (token revoked)")
    return {"success": True, "message": "Sesión cerrada"}
