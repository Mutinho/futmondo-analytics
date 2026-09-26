"""
API endpoints for user finances calculation.

Prize money (ranking, MVP, dream-team and points prizes) comes exclusively from
the ``team_prizes`` table, which is the single source of truth populated by
``DataSyncService.sync_prizes()``. That sync already enforces the business rule
that a matchday only awards ranking/MVP/dream-team prizes once every match of
the round has been played, so no prize logic is recalculated here.
"""

import logging
from typing import Dict, List

from fastapi import APIRouter, HTTPException, Query, Request

from app.core.config import CHAMPIONSHIP_ID
from app.services.data_manager_v2 import DataManagerV2
from app.services.db_connection import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_finance_config(championship_id: str, user_id: str) -> dict:
    """Get money configuration for a championship from user_championships.

    Only ``initial_budget`` is needed for the finance calculation now that all
    prize money is read pre-computed from ``team_prizes``.
    """
    db = get_db()
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        sql = db.adapt_params(
            "SELECT initial_budget FROM user_championships "
            "WHERE user_id = ? AND championship_id = ?"
        )
        cursor.execute(sql, (user_id, championship_id))
        row = cursor.fetchone()

    initial_budget = (row[0] if row and row[0] else None) or 200000000
    return {"initial_budget": initial_budget}


@router.get("/")
async def get_player_finances(
    request: Request,
    championship_id: str = Query(default=CHAMPIONSHIP_ID, description="Championship ID"),
    matchday: int = Query(default=None, description="Matchday number (optional, uses current if not provided)"),
):
    """
    Calculate money for each USER (fantasy team) as:

        total = initial_budget
              + transaction_profit
              + ranking_prize + mvp_prize + dream_team_prize + points_prize   (from team_prizes)
              + net_adjustment (punishments/bonuses)

    All prize money is read from the ``team_prizes`` table (single source of
    truth). Only fully-played matchdays contribute ranking/MVP/dream-team
    prizes there.
    """
    try:
        user = getattr(request.state, "user", None)
        user_id = user["user_id"] if user else ""
        config = _get_finance_config(championship_id, user_id)
        INITIAL_BUDGET = config["initial_budget"]

        dm = DataManagerV2(skip_init=True)

        users_data = dm.get_all_users_with_points(championship_id)
        logger.info(f"Found {len(users_data)} users in championship {championship_id}")

        if not users_data:
            logger.warning("No users found in database for championship %s", championship_id)
            return {
                "success": True,
                "championship_id": championship_id,
                "total_users": 0,
                "users": [],
            }

        # Data sources
        user_transactions = dm.get_user_transactions(championship_id)
        user_punishments_bonuses = dm.get_user_punishments_bonuses(championship_id)
        user_bonuses = dm.get_dream_team_bonus_stats(championship_id)
        # Single source of truth for all prize money
        prizes_by_team = dm.get_prizes_by_team(championship_id)
        logger.info(
            "Loaded transactions=%s, adjustments=%s, prize_teams=%s",
            len(user_transactions), len(user_punishments_bonuses), len(prizes_by_team),
        )

        # --- Build lookup tables to resolve entries by team_id/user_id/name ---
        team_lookup: Dict[str, Dict] = {}
        name_lookup: Dict[str, Dict] = {}
        get_user_info = getattr(dm, "get_user_info_from_db", None)

        def register_lookup(info: Dict):
            if not info:
                return
            for key in (info.get("team_id"), info.get("user_id")):
                if key:
                    team_lookup[key] = info
            for name in (info.get("team_name"), info.get("username")):
                if name:
                    name_lookup[name.strip().lower()] = info

        for entry in users_data:
            register_lookup(entry)

        default_info = {"team_id": None, "user_id": None, "team_name": "Unknown", "username": "Unknown"}

        for mapping in (user_transactions, user_bonuses, user_punishments_bonuses):
            for key in mapping.keys():
                if not key or key in team_lookup:
                    continue
                info = None
                if callable(get_user_info):
                    try:
                        info = get_user_info(key)
                    except Exception as lookup_err:
                        logger.debug(f"Lookup failed for key {key}: {lookup_err}")
                register_lookup(info or {**default_info, "team_id": key, "user_id": key})

        def resolve_mapping_entry(mapping: Dict, keys: List[str], team_name: str, username: str):
            for key in keys:
                if key and key in mapping:
                    return mapping[key]
            for key in keys:
                info = team_lookup.get(key)
                if info:
                    for candidate in (info.get("team_id"), info.get("user_id")):
                        if candidate and candidate in mapping:
                            return mapping[candidate]
            for name in (team_name, username):
                if name:
                    info = name_lookup.get(name.strip().lower())
                    if info:
                        for candidate in (info.get("team_id"), info.get("user_id")):
                            if candidate and candidate in mapping:
                                return mapping[candidate]
            return None

        def resolve_prizes(userteam_id: str, user_id: str) -> Dict[str, int]:
            for key in (userteam_id, user_id):
                if key and key in prizes_by_team:
                    return prizes_by_team[key]
            return {"ranking": 0, "mvp": 0, "points": 0, "dream_team": 0, "total": 0}

        # --- Aggregate finances per user ---
        user_finances = []
        for user in users_data:
            userteam_id = user.get("team_id")
            team_name = user.get("team_name", "Unknown")
            username = user.get("username", team_name)
            uid = user.get("user_id")
            total_points = user.get("total_points", 0)

            keys_to_try = [userteam_id, uid]

            transaction_data = resolve_mapping_entry(user_transactions, keys_to_try, team_name, username) or {}
            transaction_profit = transaction_data.get("transaction_profit", 0)
            total_spent = transaction_data.get("total_spent", 0)
            total_received = transaction_data.get("total_received", 0)
            transaction_count = transaction_data.get("transaction_count", 0)

            # Informative counts (money comes from team_prizes)
            bonus_data = resolve_mapping_entry(user_bonuses, keys_to_try, team_name, username) or {}
            ideal_team_count = bonus_data.get("ideal_team_count", 0)
            mvp_count = bonus_data.get("mvp_count", 0)

            # Prize money — single source of truth: team_prizes
            prizes = resolve_prizes(userteam_id, uid)
            points_money = prizes["points"]
            ranking_money = prizes["ranking"]
            mvp_bonus = prizes["mvp"]
            ideal_team_bonus = prizes["dream_team"]
            total_bonus = ideal_team_bonus + mvp_bonus

            adjustment_data = resolve_mapping_entry(user_punishments_bonuses, keys_to_try, team_name, username)
            if adjustment_data is None:
                adjustment_data = {
                    "total_punishments": 0, "total_bonuses": 0, "net_adjustment": 0,
                    "punishment_count": 0, "bonus_count": 0,
                }
                matched_sources = set()
                for name in (team_name, username):
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

            net_adjustment = adjustment_data.get("net_adjustment", 0)

            total_money = (
                INITIAL_BUDGET
                + points_money
                + transaction_profit
                + total_bonus
                + ranking_money
                + net_adjustment
            )

            user_finances.append({
                "userteam_id": userteam_id,
                "user_id": uid,
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
                "total_punishments": adjustment_data.get("total_punishments", 0),
                "total_bonuses": adjustment_data.get("total_bonuses", 0),
                "net_adjustment": net_adjustment,
                "punishment_count": adjustment_data.get("punishment_count", 0),
                "bonus_count": adjustment_data.get("bonus_count", 0),
                "total_money": total_money,
                "transaction_count": transaction_count,
            })

        user_finances.sort(key=lambda x: x["total_money"], reverse=True)

        return {
            "success": True,
            "championship_id": championship_id,
            "total_users": len(user_finances),
            "users": user_finances,
        }
    except Exception as e:
        logger.error(f"Error calculating user finances: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
