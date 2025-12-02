"""
API endpoints for championship statistics
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict
import logging
from app.services.data_manager_v2 import DataManagerV2
from app.core.config import CHAMPIONSHIP_ID

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/unique-players")
async def get_unique_players_stats(
    championship_id: str = Query(default=CHAMPIONSHIP_ID, description="Championship ID")
):
    """
    Get statistics of unique players aligned by each user/team
    Returns list of users/teams ordered by number of unique players aligned
    """
    try:
        dm = DataManagerV2()
        stats = dm.get_users_unique_players_stats(championship_id)
        
        return {
            "success": True,
            "championship_id": championship_id,
            "total_users": len(stats),
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting unique players stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unique-players/top")
async def get_top_unique_players(
    top: int = Query(default=10, ge=1, le=50, description="Number of top users to return"),
    championship_id: str = Query(default=CHAMPIONSHIP_ID, description="Championship ID")
):
    """
    Get top N users who have aligned the most unique players
    """
    try:
        dm = DataManagerV2()
        stats = dm.get_users_unique_players_stats(championship_id)
        
        return {
            "success": True,
            "championship_id": championship_id,
            "top": top,
            "stats": stats[:top]
        }
    except Exception as e:
        logger.error(f"Error getting top unique players: {e}")
        raise HTTPException(status_code=500, detail=str(e))








