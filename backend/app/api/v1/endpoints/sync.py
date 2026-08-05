"""
Sync endpoints for data synchronization status and manual triggers
"""

import logging
import threading
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from app.services.data_manager_v2 import DataManagerV2
from app.services.data_sync_service import DataSyncService
from app.services.futmondo_service import FutmondoService
from app.services.task_manager import get_task_manager
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


def _run_sync_in_background(task_id: str, sync_type: str, championship_id: str, client):
    """Worker function that runs sync in a separate thread."""
    tm = get_task_manager()
    try:
        tm.mark_running(task_id, step="initializing")

        sync_service = DataSyncService(futmondo_client=client)
        sync_service.championship_id = championship_id

        if sync_type == "all":
            # Run each step with progress updates
            tm.update_progress(task_id, "players", {"status": "running"})
            players_result = sync_service.sync_players_full()
            tm.update_progress(task_id, "players", {"status": "done", **players_result})

            tm.update_progress(task_id, "transactions", {"status": "running"})
            transactions_result = sync_service.sync_transactions()
            tm.update_progress(task_id, "transactions", {"status": "done", **transactions_result})

            tm.update_progress(task_id, "clauses", {"status": "running"})
            clauses_result = sync_service.sync_clauses()
            tm.update_progress(task_id, "clauses", {"status": "done", **clauses_result})

            tm.update_progress(task_id, "punishments_bonuses", {"status": "running"})
            punishments_result = sync_service.sync_punishments_bonuses()
            tm.update_progress(task_id, "punishments_bonuses", {"status": "done", **punishments_result})

            tm.update_progress(task_id, "dream_teams", {"status": "running"})
            dream_teams_result = sync_service.sync_dream_teams_mvps()
            tm.update_progress(task_id, "dream_teams", {"status": "done", **dream_teams_result})

            tm.update_progress(task_id, "player_performance", {"status": "running"})
            perf_result = sync_service.sync_player_performance()
            tm.update_progress(task_id, "player_performance", {"status": "done", **perf_result})

            tm.update_progress(task_id, "rosters", {"status": "running"})
            rosters_result = sync_service.sync_rosters()
            tm.update_progress(task_id, "rosters", {"status": "done", **rosters_result})

            tm.update_progress(task_id, "team_standings", {"status": "running"})
            standings_result = sync_service.sync_round_rankings()
            tm.update_progress(task_id, "team_standings", {"status": "done", **standings_result})

            tm.update_progress(task_id, "match_odds", {"status": "running"})
            odds_result = sync_service.sync_match_odds()
            tm.update_progress(task_id, "match_odds", {"status": "done", **odds_result})

            results = {
                "players": players_result,
                "transactions": transactions_result,
                "clauses": clauses_result,
                "punishments_bonuses": punishments_result,
                "dream_teams": dream_teams_result,
                "player_performance": perf_result,
                "rosters": rosters_result,
                "team_standings": standings_result,
                "match_odds": odds_result,
            }
        elif sync_type == "transactions":
            tm.update_progress(task_id, "transactions", {"status": "running"})
            results = {"transactions": sync_service.sync_transactions()}
        elif sync_type == "clauses":
            tm.update_progress(task_id, "clauses", {"status": "running"})
            results = {"clauses": sync_service.sync_clauses()}
        elif sync_type == "dream_teams":
            tm.update_progress(task_id, "dream_teams", {"status": "running"})
            results = {"dream_teams": sync_service.sync_dream_teams_mvps()}
        elif sync_type == "rosters":
            tm.update_progress(task_id, "rosters", {"status": "running"})
            results = {"rosters": sync_service.sync_rosters()}
        elif sync_type == "players":
            tm.update_progress(task_id, "players", {"status": "running"})
            results = {"players": sync_service.sync_players_full()}
        else:
            tm.mark_failed(task_id, f"Invalid sync_type: {sync_type}")
            return

        tm.mark_completed(task_id, results)
        logger.info(f"✅ Sync task {task_id} completed ({sync_type})")

    except Exception as e:
        logger.error(f"❌ Sync task {task_id} failed: {e}", exc_info=True)
        tm.mark_failed(task_id, str(e))


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


@router.get("/last-sync")
async def get_last_sync_date(
    championship_id: str = CHAMPIONSHIP_ID,
) -> Dict:
    """Devuelve la fecha de la última sincronización completa para un campeonato."""
    try:
        from app.services.db_connection import get_db
        db = get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            sql = "SELECT MAX(last_sync_date) FROM sync_metadata WHERE championship_id = ?"
            sql = db.adapt_params(sql)
            cursor.execute(sql, (championship_id,))
            row = cursor.fetchone()
            last_date = row[0] if row else None
            return {"success": True, "championship_id": championship_id, "last_sync": last_date}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/trigger")
async def trigger_sync(
    sync_type: str = "all",
    championship_id: str = CHAMPIONSHIP_ID,
    service: FutmondoService = Depends(FutmondoService)
) -> JSONResponse:
    """Trigger async data synchronization. Returns immediately with a task_id.
    
    Poll GET /sync/task/{task_id} for progress.
    
    Args:
        sync_type: "all", "transactions", "clauses", "dream_teams", "rosters", "players"
        championship_id: Championship ID to sync
    
    Returns:
        202 with task_id for polling
    """
    valid_types = ("all", "transactions", "clauses", "dream_teams", "rosters", "players")
    if sync_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sync_type: {sync_type}. Must be one of: {', '.join(valid_types)}"
        )

    try:
        service = ensure_authenticated(service)
    except HTTPException:
        raise

    tm = get_task_manager()

    # Prevent duplicate syncs
    active = tm.get_active_task(championship_id)
    if active:
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "detail": "A sync is already running for this championship",
                "task_id": active.task_id,
            }
        )

    task = tm.create_task(sync_type, championship_id)

    # Launch in background thread
    thread = threading.Thread(
        target=_run_sync_in_background,
        args=(task.task_id, sync_type, championship_id, service.client),
        daemon=True,
    )
    thread.start()

    return JSONResponse(
        status_code=202,
        content={
            "success": True,
            "task_id": task.task_id,
            "sync_type": sync_type,
            "championship_id": championship_id,
            "message": "Sync started. Poll GET /api/v1/sync/task/{task_id} for progress.",
        }
    )



@router.get("/task/{task_id}")
async def get_task_status(task_id: str) -> Dict:
    """Get the status and progress of a background sync task.
    
    Returns:
        - status: pending | running | completed | failed
        - current_step: which sync step is currently running
        - progress: dict of completed steps with their results
        - result: final results (only when completed)
        - error: error message (only when failed)
    """
    tm = get_task_manager()
    task = tm.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return {"success": True, **task.to_dict()}
