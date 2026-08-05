"""
Sync endpoints for data synchronization status and manual triggers
"""

import logging
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException
from app.services.data_manager_v2 import DataManagerV2
from app.services.data_sync_service import DataSyncService
from app.services.futmondo_service import FutmondoService
from app.core.config import CHAMPIONSHIP_ID

logger = logging.getLogger(__name__)

router = APIRouter()


def ensure_authenticated(service: FutmondoService) -> FutmondoService:
    """Ensure service is authenticated"""
    if not service.client.is_authenticated():
        logger.info("Service not authenticated, attempting auto-login...")
        try:
            if not service.login():
                logger.warning("⚠️ Auto-login failed")
                raise HTTPException(
                    status_code=401, 
                    detail="Not authenticated. Please login first."
                )
            logger.info("✅ Auto-login successful!")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Auto-login error: {e}")
            raise HTTPException(
                status_code=401, 
                detail=f"Authentication failed: {str(e)}"
            )
    return service


@router.get("/status")
async def get_sync_status() -> Dict:
    """Get synchronization status for all data types
    
    Returns:
        Dict with sync status for each data type:
        {
            "championship_id": str,
            "sync_status": {
                "transactions": {...},
                "clauses": {...},
                "dream_teams": {...},
                "rosters": {...},
                "player_performance": {...},
                "players": {...}
            }
        }
    """
    try:
        championship_id = CHAMPIONSHIP_ID
        dm = DataManagerV2()
        
        data_types = ["transactions", "clauses", "dream_teams", "rosters", "player_performance", "players"]
        
        sync_status = {}
        for data_type in data_types:
            metadata = dm.get_last_sync_metadata(championship_id, data_type)
            if metadata:
                sync_status[data_type] = {
                    "last_sync_id": metadata.get("last_sync_id"),
                    "last_sync_date": metadata.get("last_sync_date").isoformat() if metadata.get("last_sync_date") else None,
                    "last_sync_matchday": metadata.get("last_sync_matchday"),
                    "records_synced": metadata.get("records_synced", 0),
                    "sync_status": metadata.get("sync_status", "unknown"),
                    "updated_at": metadata.get("updated_at").isoformat() if metadata.get("updated_at") else None
                }
            else:
                sync_status[data_type] = {
                    "last_sync_id": None,
                    "last_sync_date": None,
                    "last_sync_matchday": None,
                    "records_synced": 0,
                    "sync_status": "never_synced",
                    "updated_at": None
                }
        
        return {
            "success": True,
            "championship_id": championship_id,
            "sync_status": sync_status
        }
        
    except Exception as e:
        logger.error(f"Error getting sync status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting sync status: {str(e)}")


@router.post("/trigger")
async def trigger_sync(
    sync_type: str = "all",
    championship_id: str = CHAMPIONSHIP_ID,
    service: FutmondoService = Depends(FutmondoService)
) -> Dict:
    """Manually trigger data synchronization
    
    Args:
        sync_type: Type of sync to trigger ("all", "transactions", "clauses", "dream_teams", "rosters", "players")
        championship_id: Championship ID to sync (defaults to configured one)
    
    Returns:
        Dict with sync results
    """
    try:
        
        # Ensure service is authenticated
        service = ensure_authenticated(service)
        
        # Create sync service
        sync_service = DataSyncService(futmondo_client=service.client)
        
        # Run requested sync
        if sync_type == "all":
            results = sync_service.sync_all()
        elif sync_type == "transactions":
            results = {"transactions": sync_service.sync_transactions()}
        elif sync_type == "clauses":
            results = {"clauses": sync_service.sync_clauses()}
        elif sync_type == "dream_teams":
            results = {"dream_teams": sync_service.sync_dream_teams_mvps()}
        elif sync_type == "rosters":
            results = {"rosters": sync_service.sync_rosters()}
        elif sync_type == "players":
            results = {"players": sync_service.sync_players_full()}
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sync_type: {sync_type}. Must be one of: all, transactions, clauses, dream_teams, rosters, players"
            )
        
        return {
            "success": True,
            "championship_id": championship_id,
            "sync_type": sync_type,
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering sync: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error triggering sync: {str(e)}")

