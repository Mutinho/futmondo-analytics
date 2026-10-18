"""
Auth request/response models.
"""

from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires
    user_id: str
    email: str
    display_name: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshBodyOptional(BaseModel):
    """Optional JSON body for /auth/refresh (native clients without cookies).

    The field is optional so a cookie-only (PWA) request carrying no body does
    not trigger a 422; the handler resolves the token across cookie, header, and
    body channels.
    """

    refresh_token: Optional[str] = None


class LogoutBodyOptional(BaseModel):
    """Optional JSON body for /auth/logout (native clients without cookies).

    Mirrors ``RefreshBodyOptional``: the body is optional so a cookie-only
    logout does not 422, and the token may arrive by cookie, header, or body.
    """

    refresh_token: Optional[str] = None


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
