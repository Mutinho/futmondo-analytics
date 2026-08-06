"""
JWT utilities — create and verify access/refresh tokens.
"""

import jwt
import uuid
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Secret key for signing tokens — MUST be set in production via env var
from app.core.config import JWT_SECRET
JWT_ALGORITHM = "HS256"

# Token lifetimes
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = 30


def create_access_token(user_id: str, email: str, futmondo_user_id: str = "") -> str:
    """Create a short-lived access token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "futmondo_uid": futmondo_user_id,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> tuple[str, str, datetime]:
    """Create a long-lived refresh token.
    
    Returns:
        (token_string, token_hash, expires_at)
    """
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    jti = uuid.uuid4().hex
    
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": now,
        "exp": expires_at,
        "jti": jti,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    return token, token_hash, expires_at


def verify_token(token: str, expected_type: str = "access") -> Optional[Dict]:
    """Verify and decode a JWT token.
    
    Returns:
        Decoded payload dict, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != expected_type:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        logger.debug("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.debug(f"Invalid token: {e}")
        return None


def hash_token(token: str) -> str:
    """Hash a token for storage (used for refresh token revocation)."""
    return hashlib.sha256(token.encode()).hexdigest()
