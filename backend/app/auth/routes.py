"""
Auth endpoints — login, refresh, logout.
"""

import os
import uuid
import logging
from fastapi import APIRouter, HTTPException, Request, Response, status, Cookie
from typing import Optional

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
from app.auth.session_store import get_session_store
from app.services.futmondo_client import FutmondoClient
from app.core.config import BASE_URL

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE_NAME = "futmondo_refresh_token"
REFRESH_COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 days in seconds
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"


def _set_refresh_cookie(response: Response, refresh_token: str):
    """Set refresh token as HttpOnly secure cookie."""
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=REFRESH_COOKIE_MAX_AGE,
        path="/auth",
    )


def _clear_refresh_cookie(response: Response):
    """Clear the refresh token cookie."""
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/auth",
    )


@router.post("/login")
async def login(body: LoginRequest, response: Response):
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
    
    # Store Futmondo session for this user (used by API endpoints)
    store = get_session_store()
    store.store_session(user_id, client, body.email, body.password)
    
    # Auto-detect championships on first login
    try:
        _auto_detect_championships(user_id, client)
    except Exception as e:
        logger.warning(f"Could not auto-detect championships: {e}")
    
    logger.info(f"✅ User logged in: {body.email} (id={user_id})")
    
    # Set refresh token as HttpOnly cookie
    _set_refresh_cookie(response, refresh_token)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user_id": user_id,
        "email": body.email,
        "display_name": display_name,
    }


@router.post("/refresh")
async def refresh(request: Request, futmondo_refresh_token: Optional[str] = Cookie(default=None)):
    """Get a new access token using the refresh token cookie."""
    
    if not futmondo_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token",
        )
    
    # Verify the refresh token signature
    payload = verify_token(futmondo_refresh_token, expected_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
        )
    
    # Check if token is revoked
    token_hash = hash_token(futmondo_refresh_token)
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
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/logout")
async def logout(response: Response, futmondo_refresh_token: Optional[str] = Cookie(default=None)):
    """Revoke the refresh token and clear cookie."""
    
    if futmondo_refresh_token:
        # Revoke refresh token
        token_hash = hash_token(futmondo_refresh_token)
        revoke_refresh_token(token_hash)
        
        # Remove Futmondo session
        payload = verify_token(futmondo_refresh_token, expected_type="refresh")
        if payload:
            store = get_session_store()
            store.remove_session(payload["sub"])
    
    # Clear the cookie
    _clear_refresh_cookie(response)
    
    logger.info("User logged out (token revoked)")
    return {"success": True, "message": "Sesión cerrada"}



def _auto_detect_championships(user_id: str, client):
    """Detect user's championships from Futmondo and save them if not yet configured."""
    import json
    from app.services.db_connection import get_db
    
    db = get_db()
    
    # Check if user already has championships configured
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        sql = "SELECT COUNT(*) FROM user_championships WHERE user_id = ?"
        sql = db.adapt_params(sql)
        cursor.execute(sql, (user_id,))
        count = cursor.fetchone()[0]
    
    if count > 0:
        # Already configured — skip
        return
    
    # Fetch active championships from Futmondo
    request_data = {
        "header": {"token": client.token, "userid": client.user_id},
        "query": {"excludeGeneral": False, "includeProphets": True},
        "answer": {}
    }
    
    try:
        resp = client.session.post(
            f"{client.base_url}/2/user/activechampionships",
            json=request_data,
            timeout=15
        )
        if resp.status_code != 200:
            logger.warning(f"Could not fetch active championships: HTTP {resp.status_code}")
            return
        
        data = resp.json()
        answer = data.get("answer", {})
        championships = answer.get("championships", [])
    except Exception as e:
        logger.warning(f"Error fetching active championships: {e}")
        return
    
    if not championships:
        return
    
    # Get league budget info for default initial_budget
    leagues = answer.get("leagues", [])
    league_budgets = {}
    for league in leagues:
        league_id = league.get("_id")
        budget = (league.get("generalSettings") or {}).get("budget", 200000000)
        if league_id:
            league_budgets[league_id] = budget
    
    # Check if there's existing config in user_championships from other users (for shared championships)
    existing_config = {}
    try:
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            # Look for config from any user for these championship IDs (legacy migration)
            sql = "SELECT championship_id, initial_budget, has_clauses, excluded_teams FROM user_championships WHERE championship_id IN ({}) LIMIT 10".format(
                ",".join(["?" for _ in range(min(len(championships), 10))])
            )
            sql = db.adapt_params(sql)
            champ_ids = [c.get("id") for c in championships[:10] if c.get("id")]
            if champ_ids:
                cursor.execute(sql, tuple(champ_ids))
                for row in cursor.fetchall():
                    existing_config[row[0]] = {
                        "initial_budget": row[1],
                        "has_clauses": bool(row[2]),
                        "excluded_teams": row[3] or "[]",
                    }
    except Exception:
        pass
    
    # Save detected championships with config from API
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        for champ in championships:
            champ_id = champ.get("id")
            champ_name = champ.get("name", "")
            league_id = champ.get("league", "")
            
            if not champ_id or not champ_name:
                continue
            
            # Priority: existing config > league default > 200M
            if champ_id in existing_config:
                initial_budget = existing_config[champ_id]["initial_budget"]
                has_clauses = existing_config[champ_id]["has_clauses"]
                excluded_teams = existing_config[champ_id]["excluded_teams"]
            else:
                initial_budget = league_budgets.get(league_id, 200000000)
                has_clauses = False
                excluded_teams = "[]"
            
            # Pro mode (from activechampionships response)
            is_pro = champ.get("pro", False)
            
            # Fetch championship-specific configuration
            money_per_point = 0
            money_per_ranking = 0
            dream_team_bonus = 0
            mvp_bonus = 0
            try:
                config_data = {
                    "header": {"token": client.token, "userid": client.user_id},
                    "query": {"championshipId": champ_id},
                    "answer": {}
                }
                config_resp = client.session.post(
                    f"{client.base_url}/2/championship/teams",
                    json=config_data, timeout=15
                )
                if config_resp.status_code == 200:
                    config_answer = config_resp.json().get("answer", {})
                    configuration = config_answer.get("configuration", {})
                    money_per_point = configuration.get("moneyPerPoint", 0)
                    money_per_ranking = configuration.get("moneyPerRanking", 0)
                    dream_team_bonus = configuration.get("dreamTeamPlayer", 0)
                    mvp_bonus = configuration.get("mvpPlayer", 0)
                    ranking_mode = configuration.get("rankingMode", "flop")
                    users_to_rank = configuration.get("usersToRank", -1)
                    # Also get budget and clauses from real config
                    if configuration.get("budget"):
                        initial_budget = configuration["budget"]
                    has_clauses = configuration.get("enableAutomaticClauses", False)
            except Exception as cfg_err:
                logger.debug(f"Could not fetch config for {champ_id}: {cfg_err}")
            
            if db.db_type in ["postgresql", "postgres"]:
                cursor.execute("""
                    INSERT INTO user_championships (user_id, championship_id, name, initial_budget, has_clauses, excluded_teams, money_per_point, money_per_ranking, dream_team_bonus, mvp_bonus, ranking_mode, users_to_rank, is_pro)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, championship_id) DO UPDATE SET is_pro = EXCLUDED.is_pro
                """, (user_id, champ_id, champ_name, initial_budget, has_clauses, excluded_teams, money_per_point, money_per_ranking, dream_team_bonus, mvp_bonus, ranking_mode, users_to_rank, is_pro))
            else:
                cursor.execute("""
                    INSERT OR REPLACE INTO user_championships (user_id, championship_id, name, initial_budget, has_clauses, excluded_teams, money_per_point, money_per_ranking, dream_team_bonus, mvp_bonus, ranking_mode, users_to_rank, is_pro)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, champ_id, champ_name, initial_budget, has_clauses, excluded_teams, money_per_point, money_per_ranking, dream_team_bonus, mvp_bonus, ranking_mode, users_to_rank, is_pro))
    
    logger.info(f"Auto-detected {len(championships)} championships for user {user_id}")
