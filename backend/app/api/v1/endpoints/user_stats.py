"""
User Statistics Endpoint
Returns statistics about users: unique players, clauses, transactions
"""

import logging
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from app.services.futmondo_service import FutmondoService
from app.services.data_manager_v2 import DataManagerV2
from app.core.config import CHAMPIONSHIP_ID

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_user_statistics(
    service: FutmondoService = Depends(FutmondoService)
) -> Dict:
    """Get user statistics including:
    - Unique players aligned
    - Clauses paid
    - Clauses received
    - Number of transactions
    """
    try:
        championship_id = CHAMPIONSHIP_ID
        dm = DataManagerV2()
        _ = service  # Dependency retained for compatibility, no direct API usage here

        unique_players_stats = dm.get_users_unique_players_stats(championship_id)
        clauses_stats = dm.get_user_clauses_stats(championship_id)
        user_transactions = dm.get_user_transactions(championship_id)
        bonus_stats = dm.get_dream_team_bonus_stats(championship_id)
        adjustments = dm.get_user_punishments_bonuses(championship_id)

        team_info_by_team = {}
        team_info_by_user = {}
        clause_name_map = {}

        with dm.db.get_connection() as conn:
            cursor = dm.db.get_cursor(conn)

            cursor.execute("SELECT t.team_id, t.team_name, t.user_id, u.username FROM teams t LEFT JOIN users u ON t.user_id = u.user_id")
            for row in cursor.fetchall():
                team_id = row[0]
                team_name = row[1] or "Unknown"
                user_id = row[2]
                username = row[3] or team_name
                info = {
                    "team_id": team_id,
                    "team_name": team_name,
                    "user_id": user_id,
                    "username": username
                }
                if team_id:
                    team_info_by_team[team_id] = info
                if user_id:
                    team_info_by_user[user_id] = info

            sql = "SELECT payer_team_id, payer_user_id, payer_name, receiver_team_id, receiver_user_id, receiver_name FROM clauses WHERE championship_id = ?"
            sql = dm.db.adapt_params(sql)
            cursor.execute(sql, (championship_id,))
            for row in cursor.fetchall():
                p_team, p_user, p_name, r_team, r_user, r_name = row
                if p_team and p_team not in team_info_by_team:
                    clause_name_map[p_team] = {"team_id": p_team, "team_name": p_name or p_team, "user_id": p_user, "username": p_name or p_team}
                if p_user and p_user not in team_info_by_user:
                    clause_name_map[p_user] = {"team_id": p_team or p_user, "team_name": p_name or p_user, "user_id": p_user, "username": p_name or p_user}
                if r_team and r_team not in team_info_by_team:
                    clause_name_map[r_team] = {"team_id": r_team, "team_name": r_name or r_team, "user_id": r_user, "username": r_name or r_team}
                if r_user and r_user not in team_info_by_user:
                    clause_name_map[r_user] = {"team_id": r_team or r_user, "team_name": r_name or r_user, "user_id": r_user, "username": r_name or r_user}

        info_cache: Dict[str, Dict] = {}

        def resolve_key(raw_key: str) -> Dict:
            if not raw_key:
                return {"team_id": None, "user_id": None, "team_name": "Unknown", "username": "Unknown"}
            if raw_key in info_cache:
                return info_cache[raw_key]
            if raw_key in team_info_by_team:
                info_cache[raw_key] = team_info_by_team[raw_key].copy()
                return info_cache[raw_key]
            if raw_key in team_info_by_user:
                info_cache[raw_key] = team_info_by_user[raw_key].copy()
                return info_cache[raw_key]
            if raw_key in clause_name_map:
                info_cache[raw_key] = clause_name_map[raw_key].copy()
                return info_cache[raw_key]
            info_cache[raw_key] = {
                "team_id": raw_key,
                "user_id": raw_key,
                "team_name": raw_key,
                "username": raw_key
            }
            return info_cache[raw_key]

        stats_by_team: Dict[str, Dict] = {}

        def get_entry(key: str) -> Dict:
            info = resolve_key(key)
            team_id = info.get("team_id") or info.get("user_id") or key
            entry = stats_by_team.get(team_id)
            if not entry:
                entry = {
                    "team_id": team_id,
                    "user_id": info.get("user_id"),
                    "team_name": info.get("team_name") or "Unknown",
                    "username": info.get("username") or info.get("team_name") or "Unknown",
                    "unique_players_count": 0,
                    "clauses_paid": 0,
                    "clauses_received": 0,
                    "total_clauses_paid": 0,
                    "total_clauses_received": 0,
                    "transaction_count": 0,
                    "total_spent": 0,
                    "total_received": 0,
                    "transaction_profit": 0,
                    "ideal_team_count": 0,
                    "mvp_count": 0,
                    "total_punishments": 0,
                    "total_bonuses": 0,
                    "net_adjustment": 0,
                    "punishment_count": 0,
                    "bonus_count": 0
                }
                stats_by_team[team_id] = entry
            else:
                if entry["team_name"] == "Unknown" and info.get("team_name"):
                    entry["team_name"] = info["team_name"]
                if entry["username"] == "Unknown" and info.get("username"):
                    entry["username"] = info["username"]
                if not entry["user_id"] and info.get("user_id"):
                    entry["user_id"] = info["user_id"]
            return entry

        for player_stat in unique_players_stats:
            team_id = player_stat.get("team_id")
            if not team_id:
                continue
            entry = get_entry(team_id)
            entry["unique_players_count"] = player_stat.get("unique_players_count", 0)

        for key, clause_stat in clauses_stats.items():
            entry = get_entry(key)
            entry["clauses_paid"] = clause_stat.get("clauses_paid", 0)
            entry["clauses_received"] = clause_stat.get("clauses_received", 0)
            entry["total_clauses_paid"] = clause_stat.get("total_paid", 0)
            entry["total_clauses_received"] = clause_stat.get("total_received", 0)

        for key, txn_stat in user_transactions.items():
            entry = get_entry(key)
            entry["transaction_count"] = txn_stat.get("transaction_count", 0)
            entry["total_spent"] = txn_stat.get("total_spent", 0)
            entry["total_received"] = txn_stat.get("total_received", 0)
            entry["transaction_profit"] = txn_stat.get("transaction_profit", 0)

        for key, bonus_stat in bonus_stats.items():
            entry = get_entry(key)
            entry["ideal_team_count"] = bonus_stat.get("ideal_team_count", 0)
            entry["mvp_count"] = bonus_stat.get("mvp_count", 0)

        for key, adj_stat in adjustments.items():
            entry = get_entry(key)
            entry["total_punishments"] = adj_stat.get("total_punishments", 0)
            entry["total_bonuses"] = adj_stat.get("total_bonuses", 0)
            entry["net_adjustment"] = adj_stat.get("net_adjustment", 0)
            entry["punishment_count"] = adj_stat.get("punishment_count", 0)
            entry["bonus_count"] = adj_stat.get("bonus_count", 0)

        merged: Dict[str, Dict] = {}
        numeric_fields = [
            "clauses_paid",
            "clauses_received",
            "total_clauses_paid",
            "total_clauses_received",
            "transaction_count",
            "total_spent",
            "total_received",
            "transaction_profit",
            "ideal_team_count",
            "mvp_count",
            "total_punishments",
            "total_bonuses",
            "net_adjustment",
            "punishment_count",
            "bonus_count",
        ]

        for entry in stats_by_team.values():
            name_key = (entry.get("team_name") or entry.get("username") or "").strip().lower()
            if name_key in merged:
                existing = merged[name_key]
                if entry.get("unique_players_count", 0) > existing.get("unique_players_count", 0):
                    for meta in ["team_id", "user_id", "team_name", "username"]:
                        if entry.get(meta):
                            existing[meta] = entry[meta]
                existing["unique_players_count"] = max(existing.get("unique_players_count", 0), entry.get("unique_players_count", 0))
                for field in numeric_fields:
                    existing[field] = existing.get(field, 0) + entry.get(field, 0)
            else:
                merged[name_key] = entry.copy()

        user_stats = list(merged.values())
        user_stats.sort(key=lambda item: (-item["unique_players_count"], -item["clauses_paid"], item["team_name"]))

        return {
            "success": True,
            "championship_id": championship_id,
            "total_users": len(user_stats),
            "users": user_stats
        }
        
    except Exception as e:
        logger.error(f"Error getting user statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting user statistics: {str(e)}")

