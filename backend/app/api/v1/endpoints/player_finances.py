"""
API endpoints for user finances calculation
"""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import Dict, List
import logging
from app.services.data_manager_v2 import DataManagerV2
from app.services.db_connection import get_db
from app.core.config import CHAMPIONSHIP_ID

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_finance_config(championship_id: str, user_id: str) -> dict:
    """Get money configuration for a championship from user_championships."""
    db = get_db()
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        sql = """SELECT initial_budget, money_per_point, money_per_ranking, dream_team_bonus, mvp_bonus, ranking_mode, users_to_rank 
                 FROM user_championships WHERE user_id = ? AND championship_id = ?"""
        sql = db.adapt_params(sql)
        cursor.execute(sql, (user_id, championship_id))
        row = cursor.fetchone()
    
    if row:
        return {
            "initial_budget": row[0] or 200000000,
            "money_per_point": row[1] or 0,
            "money_per_ranking": row[2] or 0,
            "dream_team_bonus": row[3] or 0,
            "mvp_bonus": row[4] or 0,
            "ranking_mode": row[5] or "flop",
            "users_to_rank": row[6] if row[6] is not None else -1,
        }
    
    return {
        "initial_budget": 200000000,
        "money_per_point": 0,
        "money_per_ranking": 0,
        "dream_team_bonus": 0,
        "mvp_bonus": 0,
        "ranking_mode": "flop",
        "users_to_rank": -1,
    }


def _calculate_ranking_prize(position: int, total_members: int, money_per_ranking: int, users_to_rank: int, ranking_mode: str = "top") -> int:
    """Calculate ranking prize using Futmondo's formula.
    
    Formula (from Futmondo's calculator):
    - totalPct = sum(1..N) where N = number of users to rank
    - Each position gets a ratio = (N - position + 1) / totalPct
    - Prize = money_per_ranking * ratio
    
    When ranking_mode = "flop", the prize is inverted: last place gets the most.
    
    Args:
        position: 1-based position (1 = first place)
        total_members: total number of teams in championship
        money_per_ranking: total money pool per round
        users_to_rank: how many users get ranked (-1 = all)
        ranking_mode: "top" (1st gets most) or "flop" (last gets most)
    """
    if money_per_ranking <= 0:
        return 0
    
    members = users_to_rank if users_to_rank > 0 else total_members
    if position > members:
        return 0
    
    # Sum of 1..members
    total_pct = members * (members + 1) // 2
    
    if ranking_mode == "flop":
        # Inverted: position 1 (first) gets least, position N (last) gets most
        ratio = position / total_pct
    else:
        # Normal: position 1 gets most
        ratio = (members - position + 1) / total_pct
    
    return round(money_per_ranking * ratio)


@router.get("/")
async def get_player_finances(
    request: Request,
    championship_id: str = Query(default=CHAMPIONSHIP_ID, description="Championship ID"),
    matchday: int = Query(default=None, description="Matchday number (optional, uses current if not provided)"),
):
    """
    Calculate money for each USER (fantasy team) based on:
    - Points (each point = 40,000 euros)
    - Market transactions (purchases/sales)
    - Ideal team bonus (300k per player in dream team per round)
    - MVP bonus (800k per round if user has MVP)
    
    Bonuses are awarded to the user who owned the player in the specific round
    they achieved the bonus.
    """
    try:
        # Get finance config from user's championship settings
        user = getattr(request.state, "user", None)
        user_id = user["user_id"] if user else ""
        config = _get_finance_config(championship_id, user_id)
        
        INITIAL_BUDGET = config["initial_budget"]
        POINTS_TO_EUROS = config["money_per_point"]
        IDEAL_TEAM_BONUS = config["dream_team_bonus"]
        MVP_BONUS = config["mvp_bonus"]
        MONEY_PER_RANKING = config["money_per_ranking"]
        RANKING_MODE = config["ranking_mode"]
        USERS_TO_RANK = config["users_to_rank"]
        
        dm = DataManagerV2(skip_init=True)
        
        users_data = dm.get_all_users_with_points(championship_id)
        logger.info(f"Found {len(users_data)} users in championship {championship_id}")
        
        if len(users_data) == 0:
            logger.warning("No users found in database for championship %s", championship_id)
            return {
                "success": True,
                "championship_id": championship_id,
                "total_users": 0,
                "users": []
            }
        
        user_transactions = dm.get_user_transactions(championship_id)
        logger.info(f"Found transactions for {len(user_transactions)} users")
        
        user_punishments_bonuses = dm.get_user_punishments_bonuses(championship_id)
        logger.info(f"Found punishments/bonuses for {len(user_punishments_bonuses)} users")
        user_bonuses = dm.get_dream_team_bonus_stats(championship_id)

        # Calculate ranking money from team_standings
        ranking_money_by_team: Dict[str, int] = {}
        if MONEY_PER_RANKING > 0:
            db_local = get_db()
            with db_local.get_connection() as conn:
                cursor = db_local.get_cursor(conn)
                sql = "SELECT team_id, matchday, position FROM team_standings WHERE championship_id = ? ORDER BY matchday"
                sql = db_local.adapt_params(sql)
                cursor.execute(sql, (championship_id,))
                standings_rows = cursor.fetchall()
            
            # Count total members for the formula
            total_members = len(users_data)
            
            for row in standings_rows:
                team_id = row[0]
                position = row[2]
                if position and position > 0:
                    prize = _calculate_ranking_prize(position, total_members, MONEY_PER_RANKING, USERS_TO_RANK, RANKING_MODE)
                    ranking_money_by_team[team_id] = ranking_money_by_team.get(team_id, 0) + prize

        team_lookup: Dict[str, Dict] = {}
        name_lookup: Dict[str, Dict] = {}
        get_user_info = getattr(dm, "get_user_info_from_db", None)

        def register_lookup(info: Dict):
            if not info:
                return
            team_id = info.get("team_id")
            user_id = info.get("user_id")
            team_name = info.get("team_name")
            username = info.get("username")

            if team_id:
                team_lookup[team_id] = info
            if user_id:
                team_lookup[user_id] = info
            for name in [team_name, username]:
                if name:
                    name_lookup[name.strip().lower()] = info

        for entry in users_data:
            register_lookup(entry)

        default_info = {
            "team_id": None,
            "user_id": None,
            "team_name": "Unknown",
            "username": "Unknown"
        }

        for mapping in [user_transactions, user_bonuses, user_punishments_bonuses]:
            for key in mapping.keys():
                if not key or key in team_lookup:
                    continue
                info = None
                if callable(get_user_info):
                    try:
                        info = get_user_info(key)
                    except Exception as lookup_err:
                        logger.debug(f"Lookup failed for key {key}: {lookup_err}")
                if not info:
                    info = {**default_info, "team_id": key, "user_id": key}
                register_lookup(info)

        def resolve_mapping_entry(mapping: Dict, keys: List[str], team_name: str, username: str):
            for key in keys:
                if key and key in mapping:
                    return mapping[key]
            for key in keys:
                info = team_lookup.get(key)
                if info:
                    for candidate in [info.get("team_id"), info.get("user_id")]:
                        if candidate and candidate in mapping:
                            return mapping[candidate]
            for name in [team_name, username]:
                if name:
                    info = name_lookup.get(name.strip().lower())
                    if info:
                        for candidate in [info.get("team_id"), info.get("user_id")]:
                            if candidate and candidate in mapping:
                                return mapping[candidate]
            return None
        
        user_finances = []
        
        for user in users_data:
            userteam_id = user.get("team_id")
            team_name = user.get("team_name", "Unknown")
            username = user.get("username", team_name)
            user_id = user.get("user_id")
            total_points = user.get("total_points", 0)
            
            points_money = total_points * POINTS_TO_EUROS
            
            keys_to_try = [userteam_id, user_id]
            transaction_data = resolve_mapping_entry(user_transactions, keys_to_try, team_name, username) or {}
            transaction_profit = transaction_data.get("transaction_profit", 0)
            total_spent = transaction_data.get("total_spent", 0)
            total_received = transaction_data.get("total_received", 0)
            transaction_count = transaction_data.get("transaction_count", 0)
            
            bonus_data = resolve_mapping_entry(user_bonuses, keys_to_try, team_name, username) or {
                "ideal_team_count": 0,
                "mvp_count": 0
            }
            ideal_team_count = bonus_data.get("ideal_team_count", 0)
            mvp_count = bonus_data.get("mvp_count", 0)
            
            ideal_team_bonus = ideal_team_count * IDEAL_TEAM_BONUS
            mvp_bonus = mvp_count * MVP_BONUS
            total_bonus = ideal_team_bonus + mvp_bonus
            
            # Ranking money (accumulated from all rounds)
            ranking_money = ranking_money_by_team.get(userteam_id, 0)
            if not ranking_money and user_id:
                ranking_money = ranking_money_by_team.get(user_id, 0)
            
            adjustment_data = resolve_mapping_entry(user_punishments_bonuses, keys_to_try, team_name, username)
            if adjustment_data is None:
                adjustment_data = {
                    "total_punishments": 0,
                    "total_bonuses": 0,
                    "net_adjustment": 0,
                    "punishment_count": 0,
                    "bonus_count": 0
                }
                matched_sources = set()
                for name in [team_name, username]:
                    if not name:
                        continue
                    lower_name = name.strip().lower()
                    for candidate, value in user_punishments_bonuses.items():
                        key_identifier = value.get("team_id") or value.get("user_id") or candidate
                        if key_identifier in matched_sources:
                            continue
                        candidate_lower = str(candidate).strip().lower()
                        value_name = (value.get("user_name") or "").strip().lower()
                        if candidate_lower == lower_name or value_name == lower_name:
                            adjustment_data["total_punishments"] += value.get("total_punishments", 0)
                            adjustment_data["total_bonuses"] += value.get("total_bonuses", 0)
                            adjustment_data["net_adjustment"] += value.get("net_adjustment", 0)
                            adjustment_data["punishment_count"] += value.get("punishment_count", 0)
                            adjustment_data["bonus_count"] += value.get("bonus_count", 0)
                            matched_sources.add(key_identifier)

            total_punishments = adjustment_data.get("total_punishments", 0)
            total_bonuses = adjustment_data.get("total_bonuses", 0)
            net_adjustment = adjustment_data.get("net_adjustment", 0)
            punishment_count = adjustment_data.get("punishment_count", 0)
            bonus_count = adjustment_data.get("bonus_count", 0)
            
            total_money = INITIAL_BUDGET + points_money + transaction_profit + total_bonus + ranking_money + net_adjustment
            
            user_finances.append({
                "userteam_id": userteam_id,
                "user_id": user_id,
                "team_name": team_name,
                "username": username,
                "total_points": total_points,
                "initial_budget": INITIAL_BUDGET,
                "points_money": points_money,
                "transaction_profit": transaction_profit,
                "total_spent": total_spent,
                "total_received": total_received,
                "ideal_team_count": ideal_team_count,
                "mvp_count": mvp_count,
                "ideal_team_bonus": ideal_team_bonus,
                "mvp_bonus": mvp_bonus,
                "total_bonus": total_bonus,
                "ranking_money": ranking_money,
                "total_punishments": total_punishments,
                "total_bonuses": total_bonuses,
                "net_adjustment": net_adjustment,
                "punishment_count": punishment_count,
                "bonus_count": bonus_count,
                "total_money": total_money,
                "transaction_count": transaction_count
            })
        
        # Sort by total money (descending)
        user_finances.sort(key=lambda x: x["total_money"], reverse=True)
        
        return {
            "success": True,
            "championship_id": championship_id,
            "total_users": len(user_finances),
            "users": user_finances
        }
    except Exception as e:
        logger.error(f"Error calculating user finances: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

