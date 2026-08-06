"""
Sync endpoints for data synchronization status and manual triggers
"""

import logging
import json
import threading
from datetime import datetime
from typing import Dict, List
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from app.services.data_manager_v2 import DataManagerV2
from app.services.data_sync_service import DataSyncService
from app.services.task_manager import get_task_manager
from app.services.db_connection import get_db
from app.services.sofascore_client import get_sofascore_client
from app.core.config import CHAMPIONSHIP_ID

logger = logging.getLogger(__name__)

router = APIRouter()


def _check_phantoms(championship_id: str, client, user_id: str = None) -> Dict:
    """Check for phantom players (players without registered purchase)."""
    db = get_db()
    
    excluded_teams = set()
    if user_id:
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            sql = "SELECT excluded_teams FROM user_championships WHERE user_id = ? AND championship_id = ?"
            sql = db.adapt_params(sql)
            cursor.execute(sql, (user_id, championship_id))
            row = cursor.fetchone()
            if row and row[0]:
                excluded_teams = set(json.loads(row[0]))
    
    standings = client.get_matchday_standings(championship_id)
    if not standings or standings.get('error'):
        return {"total_phantoms": 0, "roster_phantoms": [], "sold_phantoms": []}
    
    teams = standings.get('teams', standings.get('ranking', []))
    roster_phantoms = []
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        
        for team in teams:
            team_id = team.get('teamid') or team.get('id')
            team_name = team.get('teamname') or team.get('name')
            if team_id in excluded_teams:
                continue
            
            roster = client.get_userteam_roster(championship_id, team_id)
            if not roster:
                continue
            
            sql = "SELECT DISTINCT player_id FROM transactions WHERE buyer_team_id = ? AND championship_id = ?"
            sql = db.adapt_params(sql)
            cursor.execute(sql, (team_id, championship_id))
            bought_ids = {row[0] for row in cursor.fetchall()}
            
            for p in roster:
                pid = p.get('id')
                if pid and pid not in bought_ids:
                    roster_phantoms.append({
                        "team_name": team_name,
                        "player_name": p.get('name', '?'),
                        "value": p.get('value', 0),
                        "type": "roster",
                    })
    
    return {
        "total_phantoms": len(roster_phantoms),
        "roster_phantoms": roster_phantoms,
        "sold_phantoms": [],
    }


def _sync_sofascore(championship_id: str, client) -> Dict:
    """Sync Sofascore ratings for market players."""
    standings = client.get_matchday_standings(championship_id)
    if not standings or standings.get('error'):
        return {"synced": 0, "errors": 0, "total_players": 0}
    
    teams = standings.get('teams', standings.get('ranking', []))
    user_team_id = ""
    for t in teams:
        if t.get('userid') == client.user_id:
            user_team_id = t.get('teamid') or t.get('id', '')
            break
    if not user_team_id and teams:
        user_team_id = teams[0].get('teamid') or teams[0].get('id', '')
    
    # Get market players
    data = {
        'header': {'token': client.token, 'userid': client.user_id},
        'query': {'championshipId': championship_id, 'userteamId': user_team_id},
        'answer': {}
    }
    resp = client.session.post(f'{client.base_url}/1/market/players', json=data, timeout=15)
    if resp.status_code != 200:
        return {"synced": 0, "errors": 0, "total_players": 0}
    
    result = resp.json()
    answer = result.get('answer', {})
    all_players = answer if isinstance(answer, list) else answer.get('players', [])
    computer_players = [p for p in all_players if p.get('computer') is True]
    
    sofascore = get_sofascore_client()
    db = get_db()
    synced = 0
    errors = 0
    now = datetime.now()
    cache_rows = []
    
    for p in computer_players:
        player_name = p.get('name', '')
        if not player_name:
            continue
        try:
            team_hint = p.get('team', '')
            search_result = sofascore.search_player(player_name, team_hint=team_hint)
            if not search_result or not search_result.get('id'):
                errors += 1
                continue
            full_info = sofascore.get_player_full_info(search_result['id'])
            if not full_info:
                errors += 1
                continue
            cache_rows.append((
                player_name, championship_id,
                full_info.get('id'), full_info.get('name'), full_info.get('team'),
                full_info.get('rating'), full_info.get('goals'), full_info.get('assists'),
                full_info.get('appearances'), full_info.get('minutes_played'),
                full_info.get('yellow_cards'), full_info.get('red_cards'),
                full_info.get('tournament'), full_info.get('season'),
                full_info.get('position'), full_info.get('nationality'),
                full_info.get('age'), full_info.get('successful_dribbles'),
                full_info.get('accurate_passes_pct'), full_info.get('shots_on_target'),
                full_info.get('tackles'), full_info.get('interceptions'),
                full_info.get('clean_sheets'), full_info.get('saves'),
                full_info.get('sofascore_url', ''), now,
            ))
            synced += 1
        except Exception as e:
            logger.warning(f"Sofascore error for '{player_name}': {e}")
            errors += 1
    
    if cache_rows:
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            if db.db_type in ["postgresql", "postgres"]:
                from psycopg2.extras import execute_values
                raw_cursor = cursor._cursor if hasattr(cursor, '_cursor') else cursor
                # Clear old cache first
                raw_cursor.execute("DELETE FROM sofascore_cache WHERE championship_id = %s", (championship_id,))
                execute_values(raw_cursor, """
                    INSERT INTO sofascore_cache 
                    (player_name, championship_id, sofascore_id, sofascore_name, team,
                     rating, goals, assists, appearances, minutes_played,
                     yellow_cards, red_cards, tournament, season, position,
                     nationality, age, successful_dribbles, accurate_passes_pct,
                     shots_on_target, tackles, interceptions, clean_sheets, saves,
                     sofascore_url, synced_at)
                    VALUES %s
                """, cache_rows, page_size=50)
            else:
                cursor.execute("DELETE FROM sofascore_cache WHERE championship_id = ?", (championship_id,))
                cursor.executemany("""
                    INSERT INTO sofascore_cache 
                    (player_name, championship_id, sofascore_id, sofascore_name, team,
                     rating, goals, assists, appearances, minutes_played,
                     yellow_cards, red_cards, tournament, season, position,
                     nationality, age, successful_dribbles, accurate_passes_pct,
                     shots_on_target, tackles, interceptions, clean_sheets, saves,
                     sofascore_url, synced_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, cache_rows)
    
    return {"synced": synced, "errors": errors, "total_players": len(computer_players)}


def _run_sync_in_background(task_id: str, sync_type: str, championship_id: str, client, user_id: str = ""):
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

            # --- Check phantoms ---
            tm.update_progress(task_id, "phantoms", {"status": "running"})
            try:
                phantoms_result = _check_phantoms(championship_id, client, user_id)
                tm.update_progress(task_id, "phantoms", {"status": "done", **phantoms_result})
                results["phantoms"] = phantoms_result
            except Exception as ph_err:
                logger.warning(f"Phantom check failed (non-critical): {ph_err}")
                tm.update_progress(task_id, "phantoms", {"status": "done", "total_phantoms": 0, "error": str(ph_err)})
                results["phantoms"] = {"total_phantoms": 0}

            # --- Sync Sofascore ratings ---
            tm.update_progress(task_id, "sofascore", {"status": "running"})
            try:
                sofascore_result = _sync_sofascore(championship_id, client)
                tm.update_progress(task_id, "sofascore", {"status": "done", **sofascore_result})
                results["sofascore"] = sofascore_result
            except Exception as sf_err:
                logger.warning(f"Sofascore sync failed (non-critical): {sf_err}")
                tm.update_progress(task_id, "sofascore", {"status": "done", "synced": 0, "error": str(sf_err)})
                results["sofascore"] = {"synced": 0}
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
    request: Request,
    sync_type: str = "all",
    championship_id: str = CHAMPIONSHIP_ID,
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

    # Get user's Futmondo client from session store
    from app.api.v1.endpoints._helpers import get_user_futmondo_client
    client = get_user_futmondo_client(request)

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
    user_id = getattr(request.state, "user", {}).get("user_id", "")
    thread = threading.Thread(
        target=_run_sync_in_background,
        args=(task.task_id, sync_type, championship_id, client, user_id),
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
