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
    money_per_point: int = 0
    money_per_ranking: int = 0
    dream_team_bonus: int = 0
    mvp_bonus: int = 0
    ranking_mode: str = "flop"
    users_to_rank: int = -1


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
            SELECT championship_id, name, initial_budget, has_clauses, excluded_teams,
                   money_per_point, money_per_ranking, dream_team_bonus, mvp_bonus,
                   ranking_mode, users_to_rank
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
            "money_per_point": row[5] or 0,
            "money_per_ranking": row[6] or 0,
            "dream_team_bonus": row[7] or 0,
            "mvp_bonus": row[8] or 0,
            "ranking_mode": row[9] or "flop",
            "users_to_rank": row[10] if row[10] is not None else -1,
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
                INSERT INTO user_championships (user_id, championship_id, name, initial_budget, has_clauses, excluded_teams, money_per_point, money_per_ranking, dream_team_bonus, mvp_bonus, ranking_mode, users_to_rank)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, championship_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    initial_budget = EXCLUDED.initial_budget,
                    has_clauses = EXCLUDED.has_clauses,
                    excluded_teams = EXCLUDED.excluded_teams,
                    money_per_point = EXCLUDED.money_per_point,
                    money_per_ranking = EXCLUDED.money_per_ranking,
                    dream_team_bonus = EXCLUDED.dream_team_bonus,
                    mvp_bonus = EXCLUDED.mvp_bonus,
                    ranking_mode = EXCLUDED.ranking_mode,
                    users_to_rank = EXCLUDED.users_to_rank
            """, (user["user_id"], config.championship_id, config.name, config.initial_budget, config.has_clauses, excluded_json, config.money_per_point, config.money_per_ranking, config.dream_team_bonus, config.mvp_bonus, config.ranking_mode, config.users_to_rank))
        else:
            cursor.execute("""
                INSERT OR REPLACE INTO user_championships (user_id, championship_id, name, initial_budget, has_clauses, excluded_teams, money_per_point, money_per_ranking, dream_team_bonus, mvp_bonus, ranking_mode, users_to_rank)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user["user_id"], config.championship_id, config.name, config.initial_budget, config.has_clauses, excluded_json, config.money_per_point, config.money_per_ranking, config.dream_team_bonus, config.mvp_bonus, config.ranking_mode, config.users_to_rank))
    
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



@router.post("/championships/{championship_id}/resync")
async def resync_championship_config(request: Request, championship_id: str) -> Dict:
    """Resync championship configuration from Futmondo API."""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    from app.api.v1.endpoints._helpers import get_user_futmondo_client
    from app.services.db_connection import get_db
    
    client = get_user_futmondo_client(request)
    
    # Fetch config from Futmondo
    config_data = {
        "header": {"token": client.token, "userid": client.user_id},
        "query": {"championshipId": championship_id},
        "answer": {}
    }
    
    try:
        resp = client.session.post(
            f"{client.base_url}/2/championship/teams",
            json=config_data, timeout=15
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="No se pudo obtener configuración de Futmondo")
        
        answer = resp.json().get("answer", {})
        configuration = answer.get("configuration", {})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error contactando Futmondo: {str(e)}")
    
    # Extract values
    initial_budget = configuration.get("budget", 200000000)
    has_clauses = configuration.get("enableAutomaticClauses", False)
    money_per_point = configuration.get("moneyPerPoint", 0)
    money_per_ranking = configuration.get("moneyPerRanking", 0)
    dream_team_bonus = configuration.get("dreamTeamPlayer", 0)
    mvp_bonus = configuration.get("mvpPlayer", 0)
    ranking_mode = configuration.get("rankingMode", "flop")
    users_to_rank = configuration.get("usersToRank", -1)
    
    # Update in DB
    db = get_db()
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        if db.db_type in ["postgresql", "postgres"]:
            cursor.execute("""
                UPDATE user_championships SET
                    initial_budget = %s, has_clauses = %s,
                    money_per_point = %s, money_per_ranking = %s,
                    dream_team_bonus = %s, mvp_bonus = %s,
                    ranking_mode = %s, users_to_rank = %s
                WHERE user_id = %s AND championship_id = %s
            """, (initial_budget, has_clauses, money_per_point, money_per_ranking, dream_team_bonus, mvp_bonus, ranking_mode, users_to_rank, user["user_id"], championship_id))
        else:
            cursor.execute("""
                UPDATE user_championships SET
                    initial_budget = ?, has_clauses = ?,
                    money_per_point = ?, money_per_ranking = ?,
                    dream_team_bonus = ?, mvp_bonus = ?,
                    ranking_mode = ?, users_to_rank = ?
                WHERE user_id = ? AND championship_id = ?
            """, (initial_budget, has_clauses, money_per_point, money_per_ranking, dream_team_bonus, mvp_bonus, ranking_mode, users_to_rank, user["user_id"], championship_id))
    
    return {
        "success": True,
        "message": "Configuración actualizada desde Futmondo",
        "configuration": {
            "initial_budget": initial_budget,
            "has_clauses": has_clauses,
            "money_per_point": money_per_point,
            "money_per_ranking": money_per_ranking,
            "dream_team_bonus": dream_team_bonus,
            "mvp_bonus": mvp_bonus,
            "ranking_mode": ranking_mode,
            "users_to_rank": users_to_rank,
        }
    }
