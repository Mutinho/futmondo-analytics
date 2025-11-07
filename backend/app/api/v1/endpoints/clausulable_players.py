"""
API endpoint for clausulable players ranking
Returns top 20 players based on clause value analysis
"""

import logging
from typing import Dict, List
from fastapi import APIRouter, HTTPException, Query

from app.core.config import CHAMPIONSHIP_ID
from app.services.data_manager_v2 import DataManagerV2

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_clausulable_players(
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

            try:
                clause_price_val = float(clause_price)
                suggested_clause_val = float(suggested_clause)
                avg_last_five_val = float(average_last_five)
                avg_overall_val = float(average_overall)
            except (TypeError, ValueError):
                continue

            if avg_last_five_val == 0 or avg_overall_val == 0 or clause_price_val == 0:
                continue

            metric1 = clause_price_val / avg_last_five_val
            metric2 = suggested_clause_val / clause_price_val
            metric3 = clause_price_val / avg_overall_val

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
                "metric2": metric2,
                "metric3": metric3
            })

        if not scored_players:
            logger.warning("No players with valid clausulable metrics in database")
            return {
                "success": False,
                "message": "No players with valid clause metrics in database",
                "players": []
            }

        metric1_values = [p["metric1"] for p in scored_players if p["metric1"] != float('inf')]
        metric2_values = [p["metric2"] for p in scored_players]
        metric3_values = [p["metric3"] for p in scored_players if p["metric3"] != float('inf')]

        min_metric1 = min(metric1_values) if metric1_values else 0
        max_metric1 = max(metric1_values) if metric1_values else 1
        min_metric2 = min(metric2_values) if metric2_values else 0
        max_metric2 = max(metric2_values) if metric2_values else 1
        min_metric3 = min(metric3_values) if metric3_values else 0
        max_metric3 = max(metric3_values) if metric3_values else 1

        range_metric1 = max_metric1 - min_metric1 if max_metric1 != min_metric1 else 1
        range_metric2 = max_metric2 - min_metric2 if max_metric2 != min_metric2 else 1
        range_metric3 = max_metric3 - min_metric3 if max_metric3 != min_metric3 else 1

        for player in scored_players:
            if player["metric1"] == float('inf'):
                normalized_metric1 = 0.0
            else:
                normalized_metric1 = (max_metric1 - player["metric1"]) / range_metric1
                normalized_metric1 = max(0.0, min(1.0, normalized_metric1))

            normalized_metric2 = (player["metric2"] - min_metric2) / range_metric2
            normalized_metric2 = max(0.0, min(1.0, normalized_metric2))

            if player["metric3"] == float('inf'):
                normalized_metric3 = 0.0
            else:
                normalized_metric3 = (max_metric3 - player["metric3"]) / range_metric3
                normalized_metric3 = max(0.0, min(1.0, normalized_metric3))

            final_score = (
                (normalized_metric1 * (1 / 3)) +
                (normalized_metric2 * (1 / 3)) +
                (normalized_metric3 * (1 / 3))
            )

            player["normalized_metric1"] = normalized_metric1
            player["normalized_metric2"] = normalized_metric2
            player["normalized_metric3"] = normalized_metric3
            player["final_score"] = final_score

        scored_players.sort(key=lambda x: x["final_score"], reverse=True)

        result = []
        for player in scored_players:
            result.append({
                "player_id": player["player_id"],
                "player_name": player["player_name"],
                "owner_name": player["owner_name"],
                "owner_id": player["owner_id"],
                "average_last_five": round(player["average_last_five"], 2),
                "average_overall": round(player["average_overall"], 2),
                "clause_price": int(player["clause_price"]),
                "suggested_clause": int(player["suggested_clause"]),
                "metric1_score": round(player["normalized_metric1"], 4),
                "metric2_score": round(player["normalized_metric2"], 4),
                "metric3_score": round(player["normalized_metric3"], 4),
                "final_score": round(player["final_score"], 4),
                "metric1_raw": round(player["metric1"], 2),
                "metric2_raw": round(player["metric2"], 4),
                "metric3_raw": round(player["metric3"], 2)
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

