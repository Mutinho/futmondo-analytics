"""
API endpoint for clausulable players ranking
Returns top 20 players based on clause value analysis
"""

import logging
from typing import Dict, List
from fastapi import APIRouter, HTTPException, Query, Request

from app.core.config import CHAMPIONSHIP_ID
from app.services.data_manager_v2 import DataManagerV2

logger = logging.getLogger(__name__)

router = APIRouter()


def _is_clausulable_now(player: dict, now) -> bool:
    """Check if a player's clause protection period has expired."""
    from datetime import datetime, timezone
    clause_date = player.get("clause_date")
    if not clause_date:
        return True  # No date means no protection info, show it
    # Parse the date string if needed
    if isinstance(clause_date, str):
        try:
            clause_date = datetime.fromisoformat(clause_date.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return True
    # If clause_date is a naive datetime, assume UTC
    if clause_date.tzinfo is None:
        clause_date = clause_date.replace(tzinfo=timezone.utc)
    return now >= clause_date


@router.get("/")
async def get_clausulable_players(
    request: Request,
    championship_id: str = Query(default=CHAMPIONSHIP_ID, description="Championship ID")
) -> Dict:
    """Get clausulable player scores using database-stored metrics.

    Calculates a score based on:
    - clause_price / averageLastFive (lower is better - cheaper relative to recent performance)
    - suggestedClause / clause_price (higher is better - more potential value)
    - clause_price / average (lower is better - cheaper relative to overall performance)

    Returns all players sorted by final score (descending). Frontend shows top 20 and allows sorting.
    """
    try:
        dm = DataManagerV2()
        players = dm.get_clausulable_player_stats(championship_id)
        logger.info(f"Loaded {len(players)} clausulable player entries from DB for {championship_id}")

        if not players:
            return {
                "success": False,
                "message": "No clausulable player statistics available in database. Run a player sync first.",
                "players": []
            }

        # Filter out players still in protection period
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        players = [p for p in players if _is_clausulable_now(p, now)]

        # Filter out the logged-in user's own players
        try:
            user = getattr(request.state, "user", None)
            logger.info(f"request.state.user = {user}")
            if user:
                app_user_id = user.get("user_id", "")
                if app_user_id:
                    from app.services.db_connection import get_db as _get_db
                    _db = _get_db()
                    with _db.get_connection() as conn:
                        cursor = _db.get_cursor(conn)
                        cursor.execute(
                            "SELECT futmondo_team_id FROM user_championships WHERE user_id = %s AND championship_id = %s",
                            (app_user_id, championship_id)
                        )
                        row = cursor.fetchone()
                        if row and row[0]:
                            user_team_id = row[0]
                            before = len(players)
                            players = [p for p in players if p.get("owner_team_id") != user_team_id]
                            logger.info(f"Filtered user's team {user_team_id}: {before} -> {len(players)}")
        except Exception as e:
            logger.warning(f"Could not filter user's own players: {e}")

        scored_players: List[Dict] = []

        for player in players:
            clause_price = player.get("clause_price")
            suggested_clause = player.get("suggested_clause")
            average_last_five = player.get("average_last_five")
            average_overall = player.get("average_overall")

            if clause_price in (None, 0) or suggested_clause is None:
                continue
            if average_last_five in (None, 0) or average_overall in (None, 0):
                continue
            # Skip players with negative averages (they're not worth clausuring)
            if average_last_five < 0 or average_overall < 0:
                continue

            try:
                clause_price_val = float(clause_price)
                suggested_clause_val = float(suggested_clause)
                avg_last_five_val = float(average_last_five)
                avg_overall_val = float(average_overall)
            except (TypeError, ValueError):
                continue

            if avg_last_five_val <= 0 or avg_overall_val <= 0 or clause_price_val == 0:
                continue

            metric1 = clause_price_val / avg_last_five_val

            scored_players.append({
                "player_id": player.get("player_id"),
                "player_name": player.get("player_name", "Unknown"),
                "owner_name": player.get("owner_team_name") or "Free Agent",
                "owner_id": player.get("owner_team_id"),
                "average_last_five": avg_last_five_val,
                "average_overall": avg_overall_val,
                "clause_price": clause_price_val,
                "suggested_clause": suggested_clause_val,
                "metric1": metric1,
            })

        if not scored_players:
            logger.warning("No players with valid clausulable metrics in database")
            return {
                "success": False,
                "message": "No players with valid clause metrics in database",
                "players": []
            }

        metric1_values = [p["metric1"] for p in scored_players if p["metric1"] != float('inf')]
        avg_values = [p["average_last_five"] for p in scored_players]

        min_metric1 = min(metric1_values) if metric1_values else 0
        max_metric1 = max(metric1_values) if metric1_values else 1
        max_avg = max(avg_values) if avg_values else 1

        range_metric1 = max_metric1 - min_metric1 if max_metric1 != min_metric1 else 1

        for player in scored_players:
            # Metric1: clause/avg (lower = better, cheaper per point)
            if player["metric1"] == float('inf'):
                normalized_price = 0.0
            else:
                normalized_price = (max_metric1 - player["metric1"]) / range_metric1
                normalized_price = max(0.0, min(1.0, normalized_price))

            # Average normalized (higher = better)
            normalized_avg = player["average_last_five"] / max_avg if max_avg > 0 else 0

            # Score: 50% average + 50% price efficiency
            final_score = (normalized_avg * 0.50) + (normalized_price * 0.50)

            player["final_score"] = final_score

        scored_players.sort(key=lambda x: x["final_score"], reverse=True)

        # Enrich with player details (slug, position, real team) and sofascore
        from app.services.db_connection import get_db
        from app.api.v1.endpoints._sofascore_helpers import build_sofascore_map, lookup_sofascore

        db = get_db()
        player_ids = [p["player_id"] for p in scored_players]
        player_info_map = {}
        if player_ids:
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                placeholders = ",".join(["%s"] * len(player_ids))
                cursor.execute(f"SELECT player_id, name, role, role2, real_team_id, real_team_name, slug, value FROM players WHERE player_id IN ({placeholders})", tuple(player_ids))
                for row in cursor.fetchall():
                    player_info_map[row[0]] = {"role": row[2], "role2": row[3], "real_team_id": row[4], "real_team_name": row[5], "slug": row[6], "value": row[7]}

        sofascore_map = build_sofascore_map(db, championship_id)

        from app.core.constants import LALIGA_TEAM_NAMES as LALIGA_TEAMS

        result = []
        for player in scored_players:
            pinfo = player_info_map.get(player["player_id"], {})
            real_team_id = pinfo.get("real_team_id", "")
            team_name = LALIGA_TEAMS.get(real_team_id or "", "") or pinfo.get("real_team_name", "")
            sf = lookup_sofascore(sofascore_map, player["player_name"], team_name)

            result.append({
                "player_id": player["player_id"],
                "player_name": player["player_name"],
                "slug": pinfo.get("slug", ""),
                "position": pinfo.get("role", ""),
                "position2": pinfo.get("role2", ""),
                "team": team_name,
                "real_team_id": real_team_id or "",
                "owner_name": player["owner_name"],
                "owner_id": player["owner_id"],
                "average_last_five": round(player["average_last_five"], 2),
                "average_overall": round(player["average_overall"], 2),
                "clause_price": int(player["clause_price"]),
                "suggested_clause": int(player["suggested_clause"]),
                "value": pinfo.get("value", 0) or 0,
                "score": round(player["final_score"], 4),
                "sofascore_rating": sf.get("rating"),
                "sofascore_url": sf.get("url"),
                "starter_pct": sf.get("starter_pct"),
            })

        logger.info(f"Returning {len(result)} clausulable players (all analyzed) from database")

        return {
            "success": True,
            "championship_id": championship_id,
            "total_players_analyzed": len(scored_players),
            "players": result
        }

    except Exception as e:
        logger.error(f"Error getting clausulable players: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting clausulable players: {str(e)}")

