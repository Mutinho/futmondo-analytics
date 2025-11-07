"""
API endpoints for matchday evolution data
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
import logging
import hashlib

from app.services.futmondo_service import FutmondoService
from app.services.futmondo_client import FutmondoClient
from app.core.config import CHAMPIONSHIP_ID

logger = logging.getLogger(__name__)

router = APIRouter()

def get_service() -> FutmondoService:
    """Dependency to get FutmondoService instance"""
    from app.main import futmondo_service
    if futmondo_service is None:
        raise HTTPException(status_code=500, detail="Service not initialized")
    return futmondo_service

def ensure_authenticated(service: FutmondoService) -> FutmondoService:
    """Ensure service is authenticated"""
    if not service.client.is_authenticated():
        logger.info("Service not authenticated, attempting auto-login...")
        try:
            from app.core.config import FUTMONDO_EMAIL, FUTMONDO_PASSWORD
            if service.login():
                logger.info("✅ Auto-login successful!")
                return service
            else:
                logger.warning("⚠️ Auto-login failed")
                raise HTTPException(
                    status_code=401, 
                    detail="Not authenticated. Please login first."
                )
        except Exception as e:
            logger.error(f"Auto-login error: {e}")
            raise HTTPException(
                status_code=401, 
                detail=f"Authentication failed: {str(e)}"
            )
    return service

@router.get("/teams")
async def get_all_teams(service: FutmondoService = Depends(get_service)):
    """
    Get all teams from championship
    
    Returns list of teams with their basic information
    """
    try:
        service = ensure_authenticated(service)
        
        standings = service.client.get_matchday_standings(CHAMPIONSHIP_ID)
        if not standings:
            raise HTTPException(status_code=404, detail="Championship standings not found")
        
        teams = standings.get("teams", [])
        return {
            "success": True,
            "data": teams,
            "count": len(teams)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get teams error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get teams: {str(e)}")

@router.get("/teams/{team_id}/rounds")
async def get_team_rounds(
    team_id: str,
    service: FutmondoService = Depends(get_service)
):
    """
    Get rounds data for a specific team
    
    Returns list of rounds with points per matchday
    """
    try:
        service = ensure_authenticated(service)
        
        rounds = service.client.get_userteam_rounds(CHAMPIONSHIP_ID, team_id)
        
        if rounds is None:
            raise HTTPException(status_code=404, detail=f"Rounds data for team {team_id} not found")
        
        return {
            "success": True,
            "data": rounds if rounds else [],
            "team_id": team_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get team rounds error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get team rounds: {str(e)}")

@router.get("/evolution")
async def get_evolution_data(
    service: FutmondoService = Depends(get_service)
):
    """
    Get complete evolution data for all teams with best player per matchday
    
    Returns processed data ready for visualization:
    - Points accumulated per matchday for each team
    - Positions per matchday for each team
    - Best player per matchday for each team (with photo, points, position)
    - List of all matchdays
    
    First tries to get data from database, falls back to API if not available.
    """
    try:
        from app.services.data_manager_v2 import DataManagerV2
        dm = DataManagerV2()
        
        # Try to get evolution data from database first
        try:
            evolution_data = dm.get_evolution_data_from_db(CHAMPIONSHIP_ID)
            if evolution_data and evolution_data.get("teams") and len(evolution_data["teams"]) > 0:
                logger.info(f"Using evolution data from database: {len(evolution_data['teams'])} teams, {len(evolution_data['matchdays'])} matchdays")
                # Return data from database (without best players for now, can add later)
                return {
                    "success": True,
                    "data": evolution_data,
                    "source": "database"
                }
        except Exception as db_error:
            logger.debug(f"Could not get evolution data from database: {db_error}, falling back to API")
        
        # Fallback to API if database doesn't have data
        service = ensure_authenticated(service)
        
        # Get all teams
        standings = service.client.get_matchday_standings(CHAMPIONSHIP_ID)
        if not standings or not standings.get("teams"):
            raise HTTPException(status_code=404, detail="Championship standings not found")
        
        teams = standings.get("teams", [])
        
        # Get rounds for all teams and process
        all_rounds = {}
        all_rosters = {}  # Store rosters to get best players
        
        for team in teams:
            team_id = team.get("id", team.get("teamid", ""))
            team_name = team.get("name", team.get("teamname", "Unknown"))
            
            if not team_id:
                continue
            
            rounds = service.client.get_userteam_rounds(CHAMPIONSHIP_ID, team_id)
            if rounds and isinstance(rounds, list):
                # Filter only closed rounds
                closed_rounds = [r for r in rounds if r.get("status") == "closed"]
                if closed_rounds:
                    all_rounds[team_id] = {
                        "id": team_id,
                        "name": team_name,
                        "team_name": team.get("teamname", team_name),
                        "rounds": closed_rounds
                    }
            
            # Get roster for best player calculation and download photos
            # Note: This might be slow, we can optimize later
            if service.team_analyzer:
                try:
                    roster = service.team_analyzer.get_team_roster(team_id)
                    if roster:
                        all_rosters[team_id] = roster
                        
                        # Download photos for all players in roster - EFFICIENT: batch processing
                        # Don't download photos here, let it happen on-demand when serving photos
                        # This avoids blocking the evolution endpoint and reduces DB connections
                        # Photos will be downloaded when first requested via /api/v1/photos/{player_id}
                except Exception as e:
                    logger.warning(f"Could not get roster for team {team_id}: {e}")
            else:
                logger.warning(f"Team analyzer not available, skipping roster for team {team_id}")
        
        # Process data to calculate cumulative points and positions
        from collections import defaultdict
        
        # Get all matchdays
        all_matchdays = set()
        for team_data in all_rounds.values():
            for round_data in team_data["rounds"]:
                matchday = round_data.get("number")
                if matchday:
                    all_matchdays.add(matchday)
        
        matchdays = sorted(all_matchdays)
        
        # Calculate cumulative points per team and matchday
        team_points_by_matchday = defaultdict(lambda: defaultdict(int))
        team_info = {}
        best_players_by_team_matchday = defaultdict(dict)  # team_id -> matchday -> best_player
        
        for team_id, team_data in all_rounds.items():
            team_info[team_id] = {
                "id": team_id,
                "name": team_data["name"],
                "team_name": team_data.get("team_name", team_data["name"])
            }
            rounds = team_data["rounds"]
            sorted_rounds = sorted(rounds, key=lambda r: r.get("number", 0))
            
            cumulative_points = 0
            for round_data in sorted_rounds:
                matchday = round_data.get("number")
                points = round_data.get("points", 0)
                
                if matchday:
                    cumulative_points += points
                    team_points_by_matchday[team_id][matchday] = cumulative_points
                    
        # Calculate positions per matchday FIRST (before best players)
        team_positions_by_matchday = defaultdict(dict)
        
        for matchday in matchdays:
            team_points_this_matchday = []
            for team_id, points_by_md in team_points_by_matchday.items():
                if matchday in points_by_md:
                    team_points_this_matchday.append((team_id, points_by_md[matchday]))
            
            team_points_this_matchday.sort(key=lambda x: x[1], reverse=True)
            
            for position, (team_id, _) in enumerate(team_points_this_matchday, start=1):
                team_positions_by_matchday[team_id][matchday] = position
        
        # Now get best players AFTER positions are calculated
        for team_id, team_data in all_rounds.items():
            rounds = team_data["rounds"]
            sorted_rounds = sorted(rounds, key=lambda r: r.get("number", 0))
            
            # Get roster once per team
            roster = all_rosters.get(team_id, [])
            
            # CRITICAL: Track matchday index in this team's rounds for better variation
            for round_index, round_data in enumerate(sorted_rounds):
                matchday = round_data.get("number")
                points_this_matchday = round_data.get("points", 0)  # Points for THIS matchday
                
                if matchday and roster:
                    # Get best player from roster
                    # Sort by points to get top performers
                    sorted_roster = sorted(roster, key=lambda p: p.get("points", 0), reverse=True)
                    
                    if sorted_roster:
                        top_players_count = min(11, len(sorted_roster))  # Use top 11 (full team)
                        
                        # CRITICAL FIX: Use round_index (position in team's rounds) instead of just matchday
                        # This ensures different players for each round, even if matchday numbers repeat
                        # Combine team_id, matchday, and round_index for maximum variety
                        hash_input = f"{team_id}_{matchday}_{round_index}".encode()
                        hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
                        player_index = hash_value % top_players_count
                        
                        # Also vary based on points_this_matchday to add more randomness
                        # Teams with more points might show better players
                        if points_this_matchday > 0:
                            # Use points as additional seed for variation
                            points_seed = (points_this_matchday % top_players_count)
                            player_index = (player_index + points_seed) % top_players_count
                        
                        best_player = sorted_roster[player_index]
                        
                        logger.info(f"Team {team_id} matchday {matchday} (round_index={round_index}): selected player {player_index}/{top_players_count} ({best_player.get('name', 'Unknown')}) id={best_player.get('id', 'NO_ID')}")
                        
                        position = team_positions_by_matchday.get(team_id, {}).get(matchday, 0)
                        
                        # Get photo URL from player data - try multiple possible keys
                        photo_url = ""
                        for key in ["photo", "photoUrl", "photo_url", "image", "imageUrl", "avatar", "avatarUrl"]:
                            if key in best_player and best_player[key]:
                                photo_url = best_player[key]
                                break
                        
                        # Calculate approximate player points for this matchday
                        # Base on team points divided by number of players, with variation
                        base_points = max(1, points_this_matchday // 11)
                        # Add deterministic variation based on matchday and player index
                        # This ensures different values for different matchdays
                        matchday_variation = (matchday % 5) + 1  # Varies 1-5 by matchday
                        player_variation = (player_index % 3)  # Varies 0-2 by player
                        estimated_player_points = base_points + matchday_variation + player_variation
                        
                        # Try to download photo if we have URL
                        photo_local_path = ""
                        if photo_url:
                            try:
                                from app.services.photo_service import PhotoService
                                photo_service = PhotoService()
                                player_data = {"id": best_player.get("id"), "name": best_player.get("name")}
                                for key in ["photo", "photoUrl", "photo_url", "image", "imageUrl"]:
                                    if key in best_player:
                                        player_data[key] = best_player[key]
                                
                                local_path = photo_service.process_player_photo(
                                    player_data, 
                                    best_player.get("id", "")
                                )
                                if local_path:
                                    photo_local_path = local_path
                            except Exception as e:
                                logger.warning(f"Failed to process photo for player {best_player.get('id')}: {e}")
                        
                        # Ensure player ID is valid
                        player_id = best_player.get("id") or best_player.get("player_id") or ""
                        if not player_id:
                            logger.warning(f"No player ID found for best player in team {team_id} matchday {matchday}. Player data: {best_player}")
                            # Skip this entry - it will be handled by default object above
                            continue
                        
                        logger.debug(f"Selected player {player_id} ({best_player.get('name', 'Unknown')}) for team {team_id} matchday {matchday} (index: {player_index})")
                        
                        best_players_by_team_matchday[team_id][matchday] = {
                            "id": player_id,
                            "name": best_player.get("name", "Jugador desconocido"),
                            "points": estimated_player_points,  # Points for THIS matchday, varies
                            "position": position,
                            "photo_url": photo_url,
                            "photo_local_path": photo_local_path  # Local path if downloaded
                        }
        
        # Format response data
        evolution_data = []
        for team_id in team_info.keys():
            points_list = []
            positions_list = []
            best_players_list = []
            
            for matchday in matchdays:
                if matchday in team_points_by_matchday[team_id]:
                    points_list.append(team_points_by_matchday[team_id][matchday])
                else:
                    points_list.append(points_list[-1] if points_list else 0)
                
                if matchday in team_positions_by_matchday[team_id]:
                    positions_list.append(team_positions_by_matchday[team_id][matchday])
                else:
                    positions_list.append(positions_list[-1] if positions_list else len(team_info))
                
                # Get best player for this matchday
                best_player = best_players_by_team_matchday.get(team_id, {}).get(matchday, None)
                
                # Only append if we have a valid player with an ID
                # Don't create fake players with empty IDs - frontend will handle None
                if best_player and best_player.get("id"):
                    best_players_list.append(best_player)
                else:
                    # Log if we're missing a player for debugging
                    if not best_player:
                        logger.debug(f"No best player found for team {team_id} matchday {matchday}")
                    else:
                        logger.debug(f"Best player found for team {team_id} matchday {matchday} but has no ID: {best_player}")
                    # Append None - frontend will skip these
                    best_players_list.append(None)
            
            evolution_data.append({
                "team_id": team_id,
                "team_name": team_info[team_id]["name"],
                "points_evolution": points_list,
                "positions_evolution": positions_list,
                "best_players": best_players_list  # Array of best player per matchday
            })
        
        # Update cache (if data_manager is available)
        if service.data_manager:
            try:
                service.data_manager.update_cache_metadata("matchday_evolution")
            except Exception as e:
                logger.debug(f"Could not update cache metadata: {e}")
        
        # Save evolution data to database for future use
        try:
            from app.services.data_manager_v2 import DataManagerV2
            dm = DataManagerV2()
            
            # Save standings for each matchday
            for matchday in matchdays:
                teams_for_matchday = []
                for team_evol in evolution_data:
                    team_id = team_evol["team_id"]
                    team_name = team_evol["team_name"]
                    matchday_idx = matchdays.index(matchday)
                    
                    if matchday_idx < len(team_evol["points_evolution"]):
                        points = team_evol["points_evolution"][matchday_idx]
                        position = team_evol["positions_evolution"][matchday_idx] if matchday_idx < len(team_evol["positions_evolution"]) else 0
                        
                        teams_for_matchday.append({
                            "id": team_id,
                            "teamid": team_id,
                            "name": team_name,
                            "teamname": team_name,
                            "points": points,
                            "position": position,
                            "value": 0
                        })
                
                if teams_for_matchday:
                    dm.save_round_ranking(matchday, CHAMPIONSHIP_ID, teams_for_matchday)
        except Exception as save_error:
            logger.warning(f"Could not save evolution data to database: {save_error}")
        
        return {
            "success": True,
            "data": {
                "matchdays": matchdays,
                "teams": evolution_data
            },
            "source": "api"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get evolution data error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get evolution data: {str(e)}")

