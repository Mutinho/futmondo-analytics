"""
Initialize endpoint - Populates database with data from all API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict
import logging
from app.services.data_initializer import DataInitializer

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/initialize")
async def initialize_data(
    background_tasks: BackgroundTasks,
    force_refresh: bool = False
) -> Dict:
    """Initialize database with data from all API endpoints
    
    Args:
        force_refresh: If True, bypasses cache and fetches fresh data
        background_tasks: FastAPI background tasks
        
    Returns:
        Status message and initial results
    """
    try:
        initializer = DataInitializer()
        
        # Run in background to avoid timeout
        def run_initialization():
            try:
                results = initializer.initialize_all_data(force_refresh=force_refresh)
                logger.info(f"Initialization complete: {results}")
            except Exception as e:
                logger.error(f"Initialization failed: {e}")
        
        background_tasks.add_task(run_initialization)
        
        return {
            "status": "initialization_started",
            "message": "Data initialization started in background. Check logs for progress.",
            "force_refresh": force_refresh
        }
    except Exception as e:
        logger.error(f"Failed to start initialization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def initialize_data_sync(
    force_refresh: bool = False
) -> Dict:
    """Initialize database synchronously (may take a while)
    
    Args:
        force_refresh: If True, bypasses cache and fetches fresh data
        
    Returns:
        Results dictionary with status of each data fetch operation
    """
    try:
        initializer = DataInitializer()
        results = initializer.initialize_all_data(force_refresh=force_refresh)
        return {
            "status": "complete",
            "results": results
        }
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/populate-players")
async def populate_players() -> Dict:
    """Populate players table from championship players API
    
    This ensures all players exist in the database before processing photos.
    
    Returns:
        Status message and count of players saved
    """
    try:
        from app.services.futmondo_service import FutmondoService
        from app.services.data_manager_v2 import DataManagerV2
        from app.core.config import CHAMPIONSHIP_ID
        
        service = FutmondoService()
        
        # Ensure authenticated
        if not service.client.is_authenticated():
            if not service.login():
                raise HTTPException(status_code=401, detail="Failed to authenticate")
        
        # Fetch championship players
        logger.info("Fetching championship players...")
        players = service.client.get_championship_players(CHAMPIONSHIP_ID)
        
        if not players:
            raise HTTPException(status_code=404, detail="No players found")
        
        # Save players using DataManagerV2
        logger.info(f"Saving {len(players)} players to database...")
        dm = DataManagerV2()
        dm.save_players(players.get("players", []))
        
        return {
            "status": "success",
            "message": f"Populated {len(players)} players in database",
            "players_count": len(players)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to populate players: {e}")
        raise HTTPException(status_code=500, detail=str(e))

