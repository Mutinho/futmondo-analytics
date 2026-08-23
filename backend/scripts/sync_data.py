#!/usr/bin/env python3
"""
Data Synchronization Script (Multi-Championship)
Runs incremental and full data synchronization from Futmondo API to database.
Iterates over all active championships, then runs Sofascore once at the end.
"""
# Early flush to confirm process starts (visible in Fly.io logs immediately)
print("sync_data.py starting...", flush=True)

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.data_sync_service import DataSyncService
from app.services.futmondo_client import FutmondoClient
from app.services.db_connection import get_db
from app.core.config import FUTMONDO_EMAIL, FUTMONDO_PASSWORD, CHAMPIONSHIP_ID

# Configure logging with flush to stdout (critical for Fly.io log capture)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)
# Force flush on every log line
for handler in logging.root.handlers:
    handler.flush = handler.stream.flush if hasattr(handler, 'stream') else lambda: None

logger = logging.getLogger(__name__)


def get_active_championship_ids(client):
    """Get championship IDs to sync by cross-referencing Futmondo API with DB.
    
    1. Calls /2/user/activechampionships to get championships the user belongs to
    2. Queries DB for DISTINCT championship_id from user_championships
    3. Returns the intersection (user is member AND championship is configured in app)
    4. Fallback: returns [CHAMPIONSHIP_ID] from config if anything fails
    
    Args:
        client: Authenticated FutmondoClient instance
        
    Returns:
        List of championship ID strings
    """
    fallback = [CHAMPIONSHIP_ID] if CHAMPIONSHIP_ID else []
    
    # Step 1: Get championships from Futmondo API
    api_championship_ids = set()
    try:
        request_data = {
            "header": {"token": client.token, "userid": client.user_id},
            "query": {"excludeGeneral": False, "includeProphets": True},
            "answer": {}
        }
        resp = client.session.post(
            f"{client.base_url}/2/user/activechampionships",
            json=request_data,
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            championships = data.get("answer", {}).get("championships", [])
            api_championship_ids = {c.get("id") for c in championships if c.get("id")}
            logger.info(f"Futmondo API: user has {len(api_championship_ids)} active championships")
        else:
            logger.warning(f"Failed to fetch active championships from API: HTTP {resp.status_code}")
    except Exception as e:
        logger.warning(f"Error fetching active championships from API: {e}")
    
    if not api_championship_ids:
        logger.warning("Could not get championships from API, using fallback")
        return fallback
    
    # Step 2: Get championships configured in the app (DB)
    db_championship_ids = set()
    try:
        db = get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            sql = "SELECT DISTINCT championship_id FROM user_championships"
            cursor.execute(sql)
            db_championship_ids = {row[0] for row in cursor.fetchall() if row[0]}
            logger.info(f"Database: {len(db_championship_ids)} championships configured in app")
    except Exception as e:
        logger.warning(f"Error querying championships from DB: {e}")
    
    if not db_championship_ids:
        logger.warning("Could not get championships from DB, using API list directly")
        return list(api_championship_ids)
    
    # Step 3: Intersection — championships where user is member AND configured in app
    active_ids = list(api_championship_ids & db_championship_ids)
    
    if not active_ids:
        logger.warning("No intersection between API and DB championships, using API list")
        return list(api_championship_ids)
    
    return active_ids


def sync_sofascore(championship_id, client):
    """Run Sofascore ratings sync using the same logic as the HTTP endpoint."""
    from app.api.v1.endpoints.sync import _sync_sofascore
    logger.info("Starting Sofascore sync...")
    logger.info(f"  Using championship {championship_id} for player list")
    try:
        result = _sync_sofascore(championship_id, client)
        synced = result.get("synced", 0)
        errors = result.get("errors", 0)
        logger.info(f"  Sofascore: done - {synced} synced, {errors} errors")
        return {"status": "done", "synced": synced, "errors": errors}
    except Exception as e:
        logger.warning(f"  Sofascore: ERROR - {e}")
        return {"status": "error", "error": str(e), "synced": 0}


def sync_championship(championship_id, client):
    """Run full sync for a single championship.
    
    Returns:
        Tuple of (results_dict, players_synced_count)
    """
    sync_service = DataSyncService(futmondo_client=client)
    sync_service.championship_id = championship_id
    
    # Ensure championship record exists in DB
    try:
        sync_service.dm.ensure_championship_exists(championship_id)
    except Exception as e:
        logger.debug(f"Could not ensure championship exists: {e}")
    
    results = sync_service.sync_all()
    
    # Update sync_metadata for this championship
    try:
        from datetime import datetime
        sync_service.dm.update_sync_metadata(
            championship_id=championship_id,
            data_type="all",
            last_sync_id="",
            last_sync_date=datetime.now(),
            records_synced=0,
            sync_duration_seconds=0,
            sync_status="success",
        )
    except Exception as e:
        logger.warning(f"Could not update sync_metadata for {championship_id}: {e}")
    
    # Count players synced
    players_synced = 0
    players_result = results.get("players", {})
    if players_result.get("status") != "error":
        players_synced = players_result.get("records_synced", 0)
    
    return results, players_synced


def main():
    """Main sync function — multi-championship with resilience"""
    try:
        logger.info("=" * 60)
        logger.info("Starting data synchronization (multi-championship)")
        logger.info("=" * 60)
        
        # Initialize Futmondo client and authenticate
        client = FutmondoClient(FUTMONDO_EMAIL, FUTMONDO_PASSWORD)
        if not client.is_authenticated():
            logger.info("Authenticating...")
            if not client.login():
                logger.error("Failed to authenticate with Futmondo")
                sys.exit(1)
            logger.info("Authentication successful")
        
        # Get active championship IDs
        championship_ids = get_active_championship_ids(client)
        if not championship_ids:
            logger.error("No championships found to sync")
            sys.exit(1)
        
        logger.info(f"Found {len(championship_ids)} active championships to sync: {championship_ids}")
        
        # --- Per-championship sync loop ---
        successes = 0
        failures = 0
        all_results = {}
        best_championship_id = championship_ids[0]
        best_players_count = 0
        
        for i, champ_id in enumerate(championship_ids, 1):
            logger.info("")
            logger.info("=" * 60)
            logger.info(f"Syncing championship {i}/{len(championship_ids)}: {champ_id}")
            logger.info("=" * 60)
            
            try:
                results, players_synced = sync_championship(champ_id, client)
                all_results[champ_id] = results
                
                # Track the championship with most players (for Sofascore later)
                if players_synced > best_players_count:
                    best_players_count = players_synced
                    best_championship_id = champ_id
                
                # Check if any critical step failed
                has_critical_error = False
                for step_name, step_result in results.items():
                    if step_result.get("status") == "error":
                        has_critical_error = True
                        break
                
                if has_critical_error:
                    logger.warning(f"Championship {champ_id}: completed with errors")
                    # Still count as success if at least some data was synced
                    if players_synced > 0:
                        successes += 1
                    else:
                        failures += 1
                else:
                    logger.info(f"Championship {champ_id}: sync complete ({players_synced} players)")
                    successes += 1
                    
            except Exception as e:
                logger.error(f"Championship {champ_id}: FAILED - {e}", exc_info=True)
                failures += 1
                all_results[champ_id] = {"error": str(e)}
        
        # --- Sofascore sync (once, using best championship) ---
        sofascore_result = None
        if "--skip-sofascore" not in sys.argv:
            logger.info("")
            logger.info("=" * 60)
            logger.info("Running Sofascore sync (once for all championships)")
            logger.info("=" * 60)
            sofascore_result = sync_sofascore(best_championship_id, client)
        else:
            logger.info("Skipping Sofascore sync (--skip-sofascore flag)")
        
        # --- Final summary ---
        logger.info("")
        logger.info("=" * 60)
        logger.info("SYNCHRONIZATION SUMMARY")
        logger.info("=" * 60)
        
        for champ_id, results in all_results.items():
            if isinstance(results, dict) and "error" not in results:
                logger.info(f"")
                logger.info(f"  Championship: {champ_id}")
                for sync_type, result in results.items():
                    status = result.get("status", "unknown")
                    records = result.get("records_synced", result.get("synced", 0))
                    duration = result.get("duration_seconds", 0)
                    if status == "error":
                        error = result.get("error", "Unknown error")
                        logger.error(f"    {sync_type}: ERROR - {error}")
                    else:
                        logger.info(f"    {sync_type}: {status} - {records} records in {duration:.2f}s")
            else:
                error = results.get("error", "Unknown") if isinstance(results, dict) else str(results)
                logger.error(f"  Championship {champ_id}: FAILED - {error}")
        
        if sofascore_result:
            logger.info(f"")
            logger.info(f"  Sofascore: {sofascore_result.get('status', 'unknown')} - {sofascore_result.get('synced', 0)} synced")
        
        logger.info("")
        total = successes + failures
        if failures == 0:
            logger.info(f"✅ Sync complete: {successes}/{total} championships OK")
        elif successes > 0:
            logger.warning(f"⚠️  Sync partial: {successes}/{total} championships OK, {failures} failed")
        else:
            logger.error(f"❌ Sync failed: 0/{total} championships succeeded")
        
        logger.info("=" * 60)
        
        # Exit 0 if at least one championship succeeded
        sys.exit(0 if successes > 0 else 1)
        
    except Exception as e:
        logger.error(f"Synchronization failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
