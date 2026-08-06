"""
API endpoints for matchday evolution data
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, List, Optional
import logging

from app.core.config import CHAMPIONSHIP_ID
from app.api.v1.endpoints._helpers import get_user_futmondo_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/teams")
async def get_all_teams(request: Request):
    """Get all teams from championship"""
    try:
        client = get_user_futmondo_client(request)
        standings = client.get_matchday_standings(CHAMPIONSHIP_ID)
        if not standings:
            raise HTTPException(status_code=404, detail="Championship standings not found")
        
        teams = standings.get("teams", [])
        return {"success": True, "data": teams, "count": len(teams)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get teams error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get teams: {str(e)}")


@router.get("/teams/{team_id}/rounds")
async def get_team_rounds(request: Request, team_id: str):
    """Get rounds data for a specific team"""
    try:
        client = get_user_futmondo_client(request)
        rounds = client.get_userteam_rounds(CHAMPIONSHIP_ID, team_id)
        
        if rounds is None:
            raise HTTPException(status_code=404, detail=f"Rounds data for team {team_id} not found")
        
        return {"success": True, "data": rounds if rounds else [], "team_id": team_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get team rounds error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get team rounds: {str(e)}")


@router.get("/evolution")
async def get_evolution_data(request: Request):
    """Get complete evolution data for all teams.
    
    First tries database, falls back to API.
    """
    try:
        from app.services.data_manager_v2 import DataManagerV2
        dm = DataManagerV2(skip_init=True)
        
        # Try database first
        try:
            evolution_data = dm.get_evolution_data_from_db(CHAMPIONSHIP_ID)
            if evolution_data and evolution_data.get("teams") and len(evolution_data["teams"]) > 0:
                return {"success": True, "data": evolution_data}
        except Exception as db_err:
            logger.debug(f"DB evolution fallback: {db_err}")
        
        # Fallback: fetch from API
        client = get_user_futmondo_client(request)
        standings = client.get_matchday_standings(CHAMPIONSHIP_ID)
        if not standings:
            return {"success": True, "data": {"teams": [], "matchdays": []}}
        
        teams = standings.get("teams", [])
        if not teams:
            return {"success": True, "data": {"teams": [], "matchdays": []}}
        
        # Build evolution from rounds
        evolution_teams = []
        all_matchdays = set()
        
        for team in teams:
            team_id = team.get("id", team.get("teamid", ""))
            team_name = team.get("teamname", team.get("name", ""))
            
            rounds = client.get_userteam_rounds(CHAMPIONSHIP_ID, team_id) or []
            
            points_by_matchday = {}
            accumulated = 0
            for r in rounds:
                matchday = r.get("number", 0)
                pts = r.get("points", 0)
                accumulated += pts
                points_by_matchday[matchday] = accumulated
                all_matchdays.add(matchday)
            
            evolution_teams.append({
                "team_id": team_id,
                "team_name": team_name,
                "points_by_matchday": points_by_matchday,
            })
        
        return {
            "success": True,
            "data": {
                "teams": evolution_teams,
                "matchdays": sorted(all_matchdays),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Evolution data error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get evolution data: {str(e)}")
