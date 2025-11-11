"""
API endpoints for press news generation
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Optional
import logging
from app.services.news_generator import NewsGenerator
from app.core.config import CHAMPIONSHIP_ID

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/generate/{matchday}")
async def generate_matchday_news(
    matchday: int,
    championship_id: str = Query(default=CHAMPIONSHIP_ID, description="Championship ID")
):
    """
    Generate funny press news for a specific matchday using OpenAI
    """
    try:
        if matchday < 1:
            raise HTTPException(status_code=400, detail="Matchday must be >= 1")
        
        generator = NewsGenerator()
        result = generator.generate_matchday_news(championship_id, matchday)
        
        if "error" in result and result["error"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "championship_id": championship_id,
            "matchday": matchday,
            "news": result.get("news", "")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating matchday news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/matchday/{matchday}/data")
async def get_matchday_data(
    matchday: int,
    championship_id: str = Query(default=CHAMPIONSHIP_ID, description="Championship ID")
):
    """
    Get matchday data for news generation (without OpenAI)
    Useful for debugging or custom news generation
    """
    try:
        if matchday < 1:
            raise HTTPException(status_code=400, detail="Matchday must be >= 1")
        
        from app.services.data_manager_v2 import DataManagerV2
        dm = DataManagerV2()
        matchday_data = dm.get_matchday_data_for_news(championship_id, matchday)
        
        return {
            "success": True,
            "championship_id": championship_id,
            "matchday": matchday,
            "data": matchday_data
        }
    except Exception as e:
        logger.error(f"Error getting matchday data: {e}")
        raise HTTPException(status_code=500, detail=str(e))





