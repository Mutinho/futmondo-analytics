"""
FastAPI dependencies for authentication.
"""

from fastapi import Request, HTTPException, status
from app.auth.jwt_utils import verify_token
from typing import Dict


def get_current_user(request: Request) -> Dict:
    """Extract and verify the current user from the Authorization header.
    
    Returns:
        Dict with user info from JWT payload (sub, email, futmondo_uid)
    
    Raises:
        HTTPException 401 if token is missing or invalid
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.split(" ", 1)[1]
    payload = verify_token(token, expected_type="access")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user_id": payload["sub"],
        "email": payload.get("email", ""),
        "futmondo_uid": payload.get("futmondo_uid", ""),
    }
