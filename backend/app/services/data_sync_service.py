"""
Data Sync Service - Handles incremental and full data synchronization
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.services.data_manager_v2 import DataManagerV2
from app.services.futmondo_client import FutmondoClient
from app.core.config import (
    CHAMPIONSHIP_ID,
    LEAGUE_ID,
    FUTMONDO_EMAIL,
    FUTMONDO_PASSWORD,
)

logger = logging.getLogger(__name__)


class DataSyncService:
    """Service for synchronizing data from Futmondo API to database"""
    
    def __init__(self, futmondo_client: FutmondoClient = None):
        # Use skip_init=True so that schemas are not dropped/recreated on every
        # DataSyncService instantiation. The schema should be created once via
        # the reset endpoint or the dedicated init script.
        self.dm = DataManagerV2(skip_init=True)
        self.championship_id = CHAMPIONSHIP_ID
        self.league_id = LEAGUE_ID
        self.user_id = ""  # Set externally for per-user sync tracking
        
        # Ensure championship record exists before any sync runs
        try:
            self.dm.ensure_championship_exists(self.championship_id)
        except Exception as e:
            logger.debug(f"Could not ensure championship exists at init: {e}")

        if futmondo_client:
            self.client = futmondo_client
        else:
            # Instantiate FutmondoClient directly to avoid legacy service dependency
            self.client = FutmondoClient(FUTMONDO_EMAIL, FUTMONDO_PASSWORD)
            if not self.client.is_authenticated():
                login_ok = self.client.login()
                if not login_ok:
                    logger.error("Failed to authenticate Futmondo client for DataSyncService")

    def _find_championship(self) -> Tuple[Optional[Dict], Dict]:
        """Locate league (by LEAGUE_ID) and championship (by CHAMPIONSHIP_ID)."""
        leagues = self.client.get_league_list()
        if not leagues:
            raise Exception("Could not fetch league list")

        league_hint = None
        championship_match = None
        championship_league = None

        for league in leagues:
            if league.get("_id") == self.league_id:
                league_hint = league
            for champ in league.get("championships", []):
                if champ.get("_id") == self.championship_id:
                    championship_match = champ
                    championship_league = league
            if league_hint and championship_match:
                break

        if championship_match is None:
            for league in leagues:
                for champ in league.get("championships", []):
                    if champ.get("_id") == self.championship_id:
                        championship_match = champ
                        championship_league = league
                        break
                if championship_match:
                    break

        if championship_match is None:
            logger.warning(
                "Could not find championship %s (league hint %s) in league list",
                self.championship_id,
                self.league_id,
            )
            return league_hint or championship_league, None

        return league_hint or championship_league, championship_match
    
    def sync_transactions(self) -> Dict:
        """Sync transactions incrementally from pressroom endpoint
        
        Returns:
            Dict with sync results (records_synced, last_sync_id, duration, status)
        """
        start_time = time.time()
        logger.info("Starting incremental transaction sync...")
        
        # Ensure market_value_at_purchase and bids_json columns exist
        try:
            db = self.dm.db
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                if db.db_type in ["postgresql", "postgres"]:
                    raw = cursor._cursor if hasattr(cursor, '_cursor') else cursor
                    raw.execute("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS market_value_at_purchase INTEGER")
                    raw.execute("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS bids_json TEXT")
                else:
                    cursor.execute("ALTER TABLE transactions ADD COLUMN market_value_at_purchase INTEGER")
                    cursor.execute("ALTER TABLE transactions ADD COLUMN bids_json TEXT")
        except Exception:
            pass  # Columns already exist
        
        try:
            # Get last sync metadata
            last_sync = self.dm.get_last_sync_metadata(self.championship_id, "transactions")
            previous_last_id = last_sync.get("last_sync_id", "") if last_sync else ""
            
            logger.info(f"Last sync ID: {previous_last_id or 'None (full sync)'}")
            
            total_synced = 0
            page_count = 0
            seen_ids = set()
            newest_transaction_id = None
            pagination_from = ""  # Always start from latest
            reached_previous = False
            
            while True:
                try:
                    page_count += 1
                    logger.info(f"📰 Pressroom page {page_count} (from={pagination_from or 'start'})...")
                    
                    pressroom_data = self.client.get_pressroom_news(self.championship_id, from_id=pagination_from or None)
                    if not pressroom_data:
                        logger.info(f"📰 Page {page_count}: No response from API, stopping.")
                        break
                    
                    news_items = pressroom_data.get("news", pressroom_data.get("data", []))
                    if not news_items:
                        logger.info(f"📰 Page {page_count}: Empty news list, stopping.")
                        break
                    
                    logger.info(f"📰 Page {page_count}: Got {len(news_items)} items")
                    
                    transaction_items = []
                    for item in news_items:
                        transaction_id = item.get("_id")
                        if not transaction_id:
                            continue
                        
                        if previous_last_id and transaction_id == previous_last_id:
                            reached_previous = True
                            break
                        
                        if item.get("_player") or item.get("_buyer") or item.get("_seller"):
                            if transaction_id not in seen_ids:
                                seen_ids.add(transaction_id)
                                transaction_items.append(item)
                                if not newest_transaction_id:
                                    newest_transaction_id = transaction_id
                    
                    logger.info(f"📰 Page {page_count}: Filtered {len(transaction_items)} transactions from {len(news_items)} items")
                    
                    if transaction_items:
                        self.dm.save_pressroom_transactions(self.championship_id, transaction_items)
                        total_synced += len(transaction_items)
                        logger.info(f"📰 Page {page_count}: Saved {len(transaction_items)} transactions (total: {total_synced})")
                        
                        # Store bids data for transactions that have them
                        self._store_bids(transaction_items)
                    
                    if reached_previous:
                        logger.info("Reached previously synced transaction ID; stopping pagination")
                        break
                    
                    last_item = news_items[-1]
                    next_from = last_item.get("_id", "")
                    if not next_from or next_from == pagination_from:
                        break
                    pagination_from = next_from
                    
                    # If no new transactions were saved on this page, we can stop to avoid endless pagination
                    if not transaction_items:
                        logger.info("No new transactions on this page, stopping")
                        break
                    
                    time.sleep(0.3)  # Rate limiting
                    
                    if page_count >= 50:  # Safety limit
                        logger.warning("Page limit reached (50)")
                        break
                        
                except Exception as e:
                    logger.error(f"Error fetching pressroom page {page_count}: {e}")
                    break
            
            duration = time.time() - start_time
            status = "success" if total_synced > 0 else "no_new_data"
            last_transaction_id = newest_transaction_id or previous_last_id
            
            # Update sync metadata
            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="transactions",
                last_sync_id=last_transaction_id,
                last_sync_date=datetime.now(),
                records_synced=total_synced,
                sync_duration_seconds=duration,
                sync_status=status
            )
            
            logger.info(f"Transaction sync complete: {total_synced} records in {duration:.2f}s")
            
            # Enrich transactions with market value at purchase date
            try:
                enriched = self._enrich_market_values()
                logger.info(f"Enriched {enriched} transactions with market value")
            except Exception as enrich_err:
                logger.warning(f"Market value enrichment failed (non-critical): {enrich_err}")
            
            return {
                "status": status,
                "records_synced": total_synced,
                "last_sync_id": last_transaction_id,
                "duration_seconds": duration
            }
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Transaction sync failed: {e}", exc_info=True)
            
            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="transactions",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration
            )
            
            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration
            }
    
    def _store_bids(self, transaction_items: list):
        """Store bids JSON for transactions that have competing bids."""
        import json as _json
        db = self.dm.db
        updates = []
        for item in transaction_items:
            bids = item.get("bids", [])
            api_id = item.get("_id", "")
            if bids and api_id:
                bids_data = [{"name": b.get("u", {}).get("name", "?"), "bid": b.get("bid", 0)} for b in bids]
                updates.append((_json.dumps(bids_data), api_id))
        
        if not updates:
            return
        
        try:
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                sql = "UPDATE transactions SET bids_json = ? WHERE api_transaction_id = ?"
                sql = db.adapt_params(sql)
                for bids_json, api_id in updates:
                    cursor.execute(sql, (bids_json, api_id))
        except Exception as e:
            logger.debug(f"Could not store bids: {e}")

    def _enrich_market_values(self) -> int:
        """Fill market_value_at_purchase for transactions that don't have it yet.
        
        For each transaction with NULL market_value_at_purchase:
        1. Call /1/player/fullprofile to get price history
        2. Find the price closest to the transaction date
        3. Update the row
        
        Processes all pending transactions in batches of 20 with pauses between batches.
        
        Returns:
            Number of transactions enriched
        """
        db = self.dm.db
        enriched = 0
        
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            
            # Find transactions missing market value
            sql = """
                SELECT transaction_id, player_id, transaction_date, buyer_team_id 
                FROM transactions 
                WHERE championship_id = ? 
                AND market_value_at_purchase IS NULL
                ORDER BY transaction_date DESC
            """
            sql = db.adapt_params(sql)
            cursor.execute(sql, (self.championship_id,))
            rows = cursor.fetchall()
            
            if not rows:
                return 0
            
            logger.info(f"Enriching {len(rows)} transactions with market value...")
            
            # Cache fullprofiles to avoid duplicate calls for same player
            profile_cache = {}
            batch_count = 0
            
            for row in rows:
                txn_id, player_id, txn_date, buyer_team_id = row[0], row[1], row[2], row[3]
                
                # Purchases from market use previous day's value; sales use same day
                is_market_purchase = (buyer_team_id != 'market_team')
                
                try:
                    # Get or fetch profile
                    if player_id not in profile_cache:
                        profile = self.client.get_player_fullprofile(player_id)
                        profile_cache[player_id] = profile
                        batch_count += 1
                        time.sleep(0.5)  # Rate limiting — 500ms between API calls
                        
                        # Pause between batches of 20 to avoid detection
                        if batch_count % 20 == 0:
                            logger.info(f"  Enriched batch ({batch_count} profiles fetched), pausing 5s...")
                            time.sleep(5)
                    else:
                        profile = profile_cache[player_id]
                    
                    if not profile or 'prices' not in profile:
                        continue
                    
                    prices = profile['prices']
                    if not prices:
                        continue
                    
                    # Find price closest to transaction date
                    market_value = self._find_price_at_date(prices, txn_date, prefer_previous_day=is_market_purchase)
                    if market_value is None:
                        continue
                    
                    # Update transaction
                    update_sql = "UPDATE transactions SET market_value_at_purchase = ? WHERE transaction_id = ?"
                    update_sql = db.adapt_params(update_sql)
                    cursor.execute(update_sql, (market_value, txn_id))
                    enriched += 1
                    
                except Exception as e:
                    logger.debug(f"Could not enrich transaction {txn_id}: {e}")
                    continue
        
        return enriched
    
    def _find_price_at_date(self, prices: list, txn_date, prefer_previous_day: bool = False) -> Optional[int]:
        """Find the social price at or near a transaction date.
        
        Args:
            prices: List of {date, social, classic} dicts from fullprofile
            txn_date: Transaction date (datetime or string)
            prefer_previous_day: If True, prefer the day before (for market purchases).
                                If False, prefer same day (for sales).
        
        Returns:
            The social price value, or None if not found
        """
        from datetime import datetime as dt
        
        # Normalize txn_date to date
        if isinstance(txn_date, str):
            try:
                txn_dt = dt.fromisoformat(txn_date.replace("Z", "+00:00")).date()
            except Exception:
                return None
        elif hasattr(txn_date, 'date'):
            txn_dt = txn_date.date()
        else:
            txn_dt = txn_date
        
        best_price = None
        best_diff = None
        ideal_diff = 1 if prefer_previous_day else 0
        
        for entry in prices:
            try:
                entry_date_str = entry.get('date', '')
                entry_dt = dt.fromisoformat(entry_date_str.replace("Z", "+00:00")).date()
                diff = (txn_dt - entry_dt).days  # Positive = entry is before txn
                
                # Only consider entries from before or same day (not future)
                if diff < 0 or diff > 3:
                    continue
                
                # Prefer ideal_diff, then closest
                if best_diff is None:
                    best_diff = diff
                    best_price = entry.get('social', entry.get('classic', 0))
                elif abs(diff - ideal_diff) < abs(best_diff - ideal_diff):
                    best_diff = diff
                    best_price = entry.get('social', entry.get('classic', 0))
            except Exception:
                continue
        
        return best_price

    def sync_clauses(self) -> Dict:
        """Sync clauses incrementally from locker news endpoint

        Returns:
            Dict with sync results
        """
        start_time = time.time()
        logger.info("Starting incremental clause sync...")

        try:
            # Get last sync metadata
            last_sync = self.dm.get_last_sync_metadata(self.championship_id, "clauses")
            previous_last_id = last_sync.get("last_sync_id", "") if last_sync else ""

            logger.info(f"Last sync ID: {previous_last_id or 'None (full sync)'}")

            total_synced = 0
            page_count = 0
            seen_ids = set()
            newest_news_id = None  # Track the most recent ID (first item of first page)
            pagination_from = ""  # Always start from latest
            reached_previous = False
            consecutive_empty_pages = 0

            while True:
                try:
                    page_count += 1
                    logger.info(f"Fetching locker news page {page_count} (from={pagination_from or 'start'})...")

                    locker_news_data = self.client.get_locker_news(self.championship_id, from_id=pagination_from or None)
                    if not locker_news_data:
                        break

                    news_items = locker_news_data.get("news", locker_news_data.get("data", []))
                    if not news_items:
                        break

                    # Filter only clause items
                    clause_items = []
                    for item in news_items:
                        item_id = item.get("_id")

                        # Stop if we reach the previously synced ID
                        if previous_last_id and item_id == previous_last_id:
                            logger.info(f"Reached previously synced clause ID: {previous_last_id}")
                            reached_previous = True
                            break

                        if item.get("styp") == "clause":
                            if item_id and item_id not in seen_ids:
                                seen_ids.add(item_id)
                                clause_items.append(item)
                                # Save the very first clause ID as the newest
                                if not newest_news_id:
                                    newest_news_id = item_id

                    # Save clauses if we found any
                    if clause_items:
                        self.dm.save_clauses(self.championship_id, clause_items)
                        total_synced += len(clause_items)
                        consecutive_empty_pages = 0
                        logger.info(f"Saved {len(clause_items)} clauses from page {page_count}")
                    else:
                        consecutive_empty_pages += 1
                        logger.info(f"No clauses on page {page_count} (consecutive empty: {consecutive_empty_pages})")

                    # Stop if we reached the previous sync point
                    if reached_previous:
                        logger.info("Reached previously synced clause, stopping pagination")
                        break

                    # Stop if we've seen too many consecutive pages without clauses
                    if consecutive_empty_pages >= 5:
                        logger.info("No clauses found in 5 consecutive pages, stopping")
                        break

                    # Get last news ID for next page (oldest item on current page)
                    last_item = news_items[-1]
                    next_from = last_item.get("_id", "")
                    if not next_from or next_from == pagination_from:
                        logger.info("No more pages to fetch")
                        break
                    pagination_from = next_from

                    time.sleep(0.3)  # Rate limiting

                    if page_count >= 50:  # Safety limit
                        logger.warning("Page limit reached (50)")
                        break

                except Exception as e:
                    logger.error(f"Error fetching locker news page {page_count}: {e}")
                    break

            duration = time.time() - start_time
            status = "success" if total_synced > 0 else "no_new_data"
            # Use the newest ID (first clause of first page) as the last_sync_id
            final_last_id = newest_news_id or previous_last_id

            # Update sync metadata
            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="clauses",
                last_sync_id=final_last_id,
                last_sync_date=datetime.now(),
                records_synced=total_synced,
                sync_duration_seconds=duration,
                sync_status=status
            )

            logger.info(f"Clause sync complete: {total_synced} records in {duration:.2f}s")

            return {
                "status": status,
                "records_synced": total_synced,
                "last_sync_id": final_last_id,
                "duration_seconds": duration
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Clause sync failed: {e}", exc_info=True)

            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="clauses",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration
            )

            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration
            }

    def sync_punishments_bonuses(self) -> Dict:
        """Sync punishments and bonuses from locker news endpoint"""
        start_time = time.time()
        logger.info("Starting punishments/bonuses sync...")

        try:
            last_sync = self.dm.get_last_sync_metadata(self.championship_id, "punishments_bonuses")
            from_id = last_sync.get("last_sync_id", "") if last_sync else ""

            logger.info(f"Last sync ID: {from_id or 'None (full sync)'}")

            total_synced = 0
            page_count = 0
            seen_ids = set()
            last_news_id = from_id

            while True:
                page_count += 1
                logger.info(f"Fetching locker news page {page_count} for punishments...")

                locker_news_data = self.client.get_locker_news(self.championship_id, from_id=from_id)
                if not locker_news_data:
                    break

                news_items = locker_news_data.get("news", locker_news_data.get("data", []))
                if not news_items:
                    break

                punish_bonus_items = []
                for item in news_items:
                    if item.get("styp") in ["punish", "bonus"]:
                        news_id = item.get("_id")
                        if news_id and news_id not in seen_ids:
                            seen_ids.add(news_id)
                            punish_bonus_items.append(item)

                if not punish_bonus_items:
                    logger.info("No new punishments/bonuses, stopping")
                    break

                self.dm.save_punishments_bonuses(self.championship_id, punish_bonus_items)
                total_synced += len(punish_bonus_items)

                last_item = news_items[-1]
                last_news_id = last_item.get("_id", "")
                from_id = last_news_id

                time.sleep(0.3)
                if page_count >= 1000:
                    logger.warning("Page limit reached (1000) during punishments sync")
                    break

            duration = time.time() - start_time
            status = "success" if total_synced > 0 or from_id else "no_new_data"

            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="punishments_bonuses",
                last_sync_id=last_news_id,
                last_sync_date=datetime.now(),
                records_synced=total_synced,
                sync_duration_seconds=duration,
                sync_status=status
            )

            logger.info(f"Punishments/bonuses sync complete: {total_synced} records in {duration:.2f}s")

            return {
                "status": status,
                "records_synced": total_synced,
                "last_sync_id": last_news_id,
                "duration_seconds": duration
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Punishments/bonuses sync failed: {e}", exc_info=True)

            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="punishments_bonuses",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration
            )

            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration
            }
    
    def sync_dream_teams_mvps(self) -> Dict:
        """Sync dream teams and MVPs for new rounds only
        
        Returns:
            Dict with sync results
        """
        start_time = time.time()
        logger.info("Starting dream team/MVP sync...")
        
        try:
            # Get last sync metadata
            last_sync = self.dm.get_last_sync_metadata(self.championship_id, "dream_teams")
            last_matchday = last_sync.get("last_sync_matchday", 0) if last_sync else 0
            if not last_matchday:
                last_matchday = 0
            
            logger.info(f"Last synced matchday: {last_matchday}")
            
            league_data, championship_data = self._find_championship()

            rounds = []
            if league_data:
                rounds = league_data.get("rounds", []) or []
            if not rounds and championship_data:
                rounds = championship_data.get("rounds", []) or []

            # Map round IDs to numbers via userteam rounds
            round_numbers = {}
            try:
                teams_data = self.client.get_matchday_standings(self.championship_id)
                sample_team = None
                if teams_data:
                    team_list = teams_data.get("teams", teams_data.get("data", []))
                    if team_list:
                        sample_team = team_list[0]
                if sample_team:
                    sample_team_id = sample_team.get("id", sample_team.get("teamid"))
                    if sample_team_id:
                        user_rounds = self.client.get_userteam_rounds(self.championship_id, sample_team_id) or []
                        for idx, entry in enumerate(user_rounds, start=1):
                            round_id = entry.get("id")
                            number = entry.get("number") or idx
                            if round_id:
                                round_numbers[round_id] = number
            except Exception as map_err:
                logger.warning(f"Could not map round numbers: {map_err}")

            closed_statuses = {"closed", "finished", "completed", "complete", "past", "played"}
            closed_rounds = [
                r for r in rounds
                if str(r.get("status", "")).lower() in closed_statuses
            ]
            if not closed_rounds and round_numbers:
                closed_rounds = [
                    {"_id": round_id, "status": "closed", "number": number}
                    for round_id, number in sorted(round_numbers.items(), key=lambda x: x[1])
                ]

            rounds_to_sync = []
            for idx, r in enumerate(closed_rounds, start=1):
                round_id = r.get("_id")
                number = round_numbers.get(round_id, idx)
                if number > last_matchday:
                    rounds_to_sync.append({**r, "number": number})
            
            logger.info(f"Found {len(rounds_to_sync)} new rounds to sync (after matchday {last_matchday})")
            
            total_synced = 0
            max_matchday = last_matchday
            
            for round_data in rounds_to_sync:
                round_id = round_data.get("_id")
                matchday = round_data.get("number", 0)
                
                if not round_id:
                    continue
                
                try:
                    # Fetch dream team for this round
                    dream_team_data = self.client.get_dream_team(self.championship_id, round_id=round_id)
                    if not dream_team_data:
                        logger.warning(f"No dream team data for round {round_id}")
                        continue
                    
                    # Extract dream team players and MVP
                    dream_team_players = []
                    player_details_map: Dict[str, Dict] = {}
                    players = dream_team_data.get("players", [])
                    for player in players:
                        player_id = None
                        if isinstance(player, dict):
                            player_id = player.get("id") or player.get("_id")
                            if player_id:
                                player_details_map[player_id] = player
                        else:
                            player_id = player
                        if player_id:
                            dream_team_players.append(player_id)
                    
                    mvp_id = dream_team_data.get("mvp")
                    
                    # Save dream team and MVP
                    self.dm.save_dream_team_mvp(
                        self.championship_id,
                        round_id,
                        matchday,
                        dream_team_players,
                        mvp_id,
                        player_details=player_details_map
                    )
                    
                    total_synced += 1
                    max_matchday = max(max_matchday, matchday)
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Failed to sync dream team for round {round_id}: {e}")
                    continue
            
            duration = time.time() - start_time
            status = "success" if total_synced > 0 or last_matchday == 0 else "no_new_data"
            
            # Update sync metadata
            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="dream_teams",
                last_sync_matchday=max_matchday,
                last_sync_date=datetime.now(),
                records_synced=total_synced,
                sync_duration_seconds=duration,
                sync_status=status
            )
            
            logger.info(f"Dream team/MVP sync complete: {total_synced} rounds in {duration:.2f}s")
            
            return {
                "status": status,
                "records_synced": total_synced,
                "last_sync_matchday": max_matchday,
                "duration_seconds": duration
            }
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Dream team/MVP sync failed: {e}", exc_info=True)
            
            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="dream_teams",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration
            )
            
            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration
            }

    def sync_player_performance(self) -> Dict:
        """Sync player performance by matchday from round lineups."""
        start_time = time.time()
        logger.info("Starting player performance sync...")

        try:
            last_sync = self.dm.get_last_sync_metadata(self.championship_id, "player_performance")
            last_matchday = last_sync.get("last_sync_matchday", 0) if last_sync else 0
            last_matchday = last_matchday or 0

            logger.info(f"Last synced player performance matchday: {last_matchday}")

            standings_data = self.client.get_matchday_standings(self.championship_id)
            teams_data = standings_data.get("teams", standings_data.get("data", [])) if standings_data else []

            team_map: List[Tuple[str, str]] = []
            for team in teams_data:
                userteam_id = (
                    team.get("id")
                    or team.get("teamid")
                    or (team.get("team") or {}).get("id")
                    or (team.get("user") or {}).get("id")
                )
                team_id = (
                    team.get("teamid")
                    or team.get("teamId")
                    or (team.get("team") or {}).get("id")
                    or userteam_id
                )
                if userteam_id and team_id:
                    team_map.append((team_id, userteam_id))

            if not team_map:
                logger.warning("No teams found for player performance sync.")
                duration = time.time() - start_time

                self.dm.update_sync_metadata(
                    championship_id=self.championship_id,
                    data_type="player_performance",
                    last_sync_matchday=last_matchday,
                    last_sync_date=datetime.now(),
                    records_synced=0,
                    sync_duration_seconds=duration,
                    sync_status="no_new_data"
                )

                return {
                    "status": "no_new_data",
                    "records_synced": 0,
                    "last_sync_matchday": last_matchday,
                    "duration_seconds": duration
                }

            sample_userteam_id = team_map[0][1]
            rounds_info = self.client.get_userteam_rounds(self.championship_id, sample_userteam_id) or []
            round_id_map: Dict[int, str] = {}
            for entry in rounds_info:
                number = entry.get("number")
                round_id = entry.get("id") or entry.get("_id") or entry.get("roundId")
                if number is None or not round_id:
                    continue
                try:
                    round_number_int = int(number)
                    round_id_map[round_number_int] = round_id
                except (TypeError, ValueError):
                    continue

            if not round_id_map:
                logger.warning("Could not determine round mappings for player performance sync.")
                duration = time.time() - start_time

                self.dm.update_sync_metadata(
                    championship_id=self.championship_id,
                    data_type="player_performance",
                    last_sync_matchday=last_matchday,
                    last_sync_date=datetime.now(),
                    records_synced=0,
                    sync_duration_seconds=duration,
                    sync_status="no_new_data"
                )

                return {
                    "status": "no_new_data",
                    "records_synced": 0,
                    "last_sync_matchday": last_matchday,
                    "duration_seconds": duration
                }

            max_round = max(round_id_map.keys())
            processed_matchday = last_matchday
            total_records = 0

            for matchday in range(last_matchday + 1, max_round + 1):
                round_id = round_id_map.get(matchday)
                if not round_id:
                    logger.debug("No round ID for matchday %s, skipping.", matchday)
                    continue

                matchday_records = []

                for team_id, userteam_id in team_map:
                    try:
                        roster_data = self.client.get_user_roundlineup(
                            self.championship_id,
                            round_id,
                            userteam_id
                        )
                        if not roster_data:
                            continue

                        roster_players = roster_data.get("players", [])
                        if not isinstance(roster_players, list):
                            continue

                        for player in roster_players:
                            player_dict = player.get("player") if isinstance(player.get("player"), dict) else None
                            player_id = (
                                player.get("id")
                                or player.get("_id")
                                or (player_dict or {}).get("id")
                                or (player_dict or {}).get("_id")
                            )
                            if not player_id:
                                continue

                            raw_points = player.get("points")
                            if raw_points is None:
                                raw_points = player.get("score")
                            if raw_points is None:
                                raw_points = player.get("roundPoints")
                            if raw_points is None:
                                raw_points = player.get("matchdayPoints")
                            if raw_points is None:
                                continue
                            try:
                                points = int(raw_points)
                            except (TypeError, ValueError):
                                continue

                            value = (
                                player.get("value")
                                or player.get("marketValue")
                                or player.get("market_price")
                                or player.get("price")
                            )
                            was_best = bool(
                                player.get("bestPlayer")
                                or player.get("isBestPlayer")
                                or player.get("mvp")
                                or player.get("isMvp")
                            )

                            matchday_records.append({
                                "player_id": player_id,
                                "team_id": team_id,
                                "matchday": matchday,
                                "points": points,
                                "value": value,
                                "was_best_player": was_best,
                            })

                        time.sleep(0.05)

                    except Exception as fetch_err:
                        logger.debug(
                            "Failed to fetch round lineup for team %s (round %s): %s",
                            userteam_id,
                            round_id,
                            fetch_err
                        )
                        continue

                # Batch insert all records for this matchday
                if matchday_records:
                    self.dm.save_player_performance_batch(self.championship_id, matchday_records)
                    total_records += len(matchday_records)
                    processed_matchday = matchday

            duration = time.time() - start_time
            status = "success" if total_records > 0 else "no_new_data"

            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="player_performance",
                last_sync_matchday=processed_matchday,
                last_sync_date=datetime.now(),
                records_synced=total_records,
                sync_duration_seconds=duration,
                sync_status=status
            )

            logger.info(
                "Player performance sync complete: %s records (up to matchday %s) in %.2fs",
                total_records,
                processed_matchday,
                duration
            )

            return {
                "status": status,
                "records_synced": total_records,
                "last_sync_matchday": processed_matchday,
                "duration_seconds": duration
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Player performance sync failed: {e}", exc_info=True)

            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="player_performance",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration
            )

            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration
            }
    
    def sync_rosters(self) -> Dict:
        """Sync team rosters for new matchdays only
        
        Returns:
            Dict with sync results
        """
        start_time = time.time()
        logger.info("Starting roster sync...")
        
        try:
            # Get last sync metadata
            last_sync = self.dm.get_last_sync_metadata(self.championship_id, "rosters")
            last_matchday = last_sync.get("last_sync_matchday", 0) if last_sync else 0
            if not last_matchday:
                last_matchday = 0
            
            logger.info(f"Last synced matchday: {last_matchday}")
            
            league_data, championship_data = self._find_championship()

            rounds = []
            if league_data:
                rounds = league_data.get("rounds", []) or []
            if not rounds and championship_data:
                rounds = championship_data.get("rounds", []) or []

            round_numbers = {}
            try:
                sample_team = None
                standings_data = self.client.get_matchday_standings(self.championship_id)
                if standings_data:
                    team_list = standings_data.get("teams", standings_data.get("data", []))
                    if team_list:
                        sample_team = team_list[0]
                if sample_team:
                    sample_team_id = sample_team.get("id", sample_team.get("teamid"))
                    if sample_team_id:
                        user_rounds = self.client.get_userteam_rounds(self.championship_id, sample_team_id) or []
                        for idx, entry in enumerate(user_rounds, start=1):
                            round_id = entry.get("id")
                            number = entry.get("number") or idx
                            if round_id:
                                round_numbers[round_id] = number
            except Exception as map_err:
                logger.warning(f"Could not map round numbers for rosters: {map_err}")

            closed_statuses = {"closed", "finished", "completed", "complete", "past", "played"}
            closed_rounds = [
                r for r in rounds
                if str(r.get("status", "")).lower() in closed_statuses
            ]
            if not closed_rounds and round_numbers:
                closed_rounds = [
                    {"_id": round_id, "status": "closed", "number": number}
                    for round_id, number in sorted(round_numbers.items(), key=lambda x: x[1])
                ]

            rounds_to_sync = []
            for idx, r in enumerate(closed_rounds, start=1):
                round_id = r.get("_id")
                number = round_numbers.get(round_id, idx)
                if number > last_matchday:
                    rounds_to_sync.append({**r, "number": number})
            
            # Get teams
            championship_teams_data = self.client.get_matchday_standings(self.championship_id)
            teams = []
            if championship_teams_data:
                teams = championship_teams_data.get("teams", championship_teams_data.get("data", []))
            
            logger.info(f"Found {len(rounds_to_sync)} new rounds and {len(teams)} teams to sync")
            
            total_synced = 0
            max_matchday = last_matchday
            
            for round_data in rounds_to_sync:
                round_id = round_data.get("_id")
                matchday = round_data.get("number", 0)
                
                if not round_id:
                    continue
                
                for team in teams:
                    userteam_id = team.get("id", team.get("teamid", ""))
                    team_id = team.get("teamid", userteam_id)
                    
                    if not userteam_id:
                        continue
                    
                    try:
                        # Get roster for this round
                        roster_data = self.client.get_user_roundlineup(self.championship_id, round_id, userteam_id)
                        if not roster_data:
                            continue
                        
                        # Get players from roster (ONLY from "players", NOT from "bench")
                        roster_players = roster_data.get("players", [])
                        if roster_players:
                            self.dm.save_team_roster(self.championship_id, team_id, roster_players, matchday=matchday)
                            total_synced += 1
                        
                        time.sleep(0.1)  # Rate limiting
                        
                    except Exception as e:
                        logger.warning(f"Failed to fetch roster for team {userteam_id} in round {round_id}: {e}")
                        continue
                
                max_matchday = max(max_matchday, matchday)
            
            duration = time.time() - start_time
            status = "success" if total_synced > 0 or last_matchday == 0 else "no_new_data"
            
            # Update sync metadata
            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="rosters",
                last_sync_matchday=max_matchday,
                last_sync_date=datetime.now(),
                records_synced=total_synced,
                sync_duration_seconds=duration,
                sync_status=status
            )
            
            logger.info(f"Roster sync complete: {total_synced} rosters in {duration:.2f}s")
            
            return {
                "status": status,
                "records_synced": total_synced,
                "last_sync_matchday": max_matchday,
                "duration_seconds": duration
            }
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Roster sync failed: {e}", exc_info=True)
            
            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="rosters",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration
            )
            
            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration
            }
    
    def sync_round_rankings(self) -> Dict:
        """Sync team standings (round rankings) — always re-syncs all matchdays."""
        start_time = time.time()
        logger.info("Starting team standings sync...")

        try:
            # Always start from matchday 1 to ensure data is up-to-date
            # (matchdays with postponed games may have changed since last sync)
            last_matchday = 0

            logger.info("Syncing all standings from matchday 1")

            standings_data = self.client.get_matchday_standings(self.championship_id)
            sample_team = None
            sample_userteam_id = None
            if standings_data:
                team_list = standings_data.get("teams", standings_data.get("data", []))
                if team_list:
                    sample_team = team_list[0]
            if sample_team:
                sample_userteam_id = (
                    sample_team.get("id")
                    or sample_team.get("teamid")
                    or (sample_team.get("team") or {}).get("id")
                    or (sample_team.get("user") or {}).get("id")
                )
            if not sample_userteam_id:
                logger.warning("Could not determine a sample userteam_id for standings sync; proceeding without it.")

            round_id_map: Dict[int, str] = {}
            if sample_userteam_id:
                rounds_info = self.client.get_userteam_rounds(self.championship_id, sample_userteam_id) or []
                for entry in rounds_info:
                    number = entry.get("number")
                    round_id = entry.get("id") or entry.get("_id") or entry.get("roundId")
                    if number is None or not round_id:
                        continue
                    try:
                        round_number_int = int(number)
                        round_id_map[round_number_int] = round_id
                    except (TypeError, ValueError):
                        continue

            rounds_synced = 0
            total_records = 0
            consecutive_missing = 0
            max_rounds = 38

            for matchday in range(last_matchday + 1, max_rounds + 1):
                round_id = round_id_map.get(matchday)
                if not round_id and sample_userteam_id:
                    rounds_info = self.client.get_userteam_rounds(self.championship_id, sample_userteam_id) or []
                    for entry in rounds_info:
                        number = entry.get("number")
                        rid = entry.get("id") or entry.get("_id") or entry.get("roundId")
                        if number is None or not rid:
                            continue
                        try:
                            round_number_int = int(number)
                            round_id_map[round_number_int] = rid
                        except (TypeError, ValueError):
                            continue
                    round_id = round_id_map.get(matchday)

                try:
                    logger.info(
                        "Fetching standings for matchday %s (round_id=%s)...",
                        matchday,
                        round_id
                    )
                    ranking_data = self.client.get_round_ranking(
                        championship_id=self.championship_id,
                        round_number=matchday,
                        round_id=round_id,
                        userteam_id=sample_userteam_id
                    )

                    teams = []
                    if isinstance(ranking_data, dict):
                        teams = (
                            ranking_data.get("teams")
                            or ranking_data.get("ranking")
                            or ranking_data.get("data")
                            or []
                        )
                    elif isinstance(ranking_data, list):
                        teams = ranking_data

                    if not teams:
                        consecutive_missing += 1
                        logger.info(
                            "No data for matchday %s (consecutive misses: %s)",
                            matchday,
                            consecutive_missing
                        )
                        if consecutive_missing >= 2:
                            logger.info("Stopping standings sync due to consecutive empty responses.")
                            break
                        continue

                    consecutive_missing = 0
                    self.dm.save_round_ranking(matchday, self.championship_id, teams)
                    rounds_synced += 1
                    total_records += len(teams)

                    time.sleep(0.2)
                except Exception as round_err:
                    logger.warning(f"Failed to process standings for matchday {matchday}: {round_err}")
                    break

            current_latest = self.dm.get_latest_matchday(self.championship_id) or last_matchday
            duration = time.time() - start_time
            status = "success" if rounds_synced > 0 else "no_new_data"

            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="team_standings",
                last_sync_matchday=current_latest,
                last_sync_date=datetime.now(),
                records_synced=total_records,
                sync_duration_seconds=duration,
                sync_status=status
            )

            logger.info(
                "Team standings sync complete: %s new matchdays (%s rows) in %.2fs",
                rounds_synced,
                total_records,
                duration
            )

            return {
                "status": status,
                "rounds_synced": rounds_synced,
                "records_synced": total_records,
                "last_matchday": current_latest,
                "duration_seconds": duration
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Team standings sync failed: {e}", exc_info=True)

            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="team_standings",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration
            )

            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration
            }
    
    def _save_favorites(self, player_ids: list):
        """Save user's favorite player IDs for the current championship.
        
        Replaces existing favorites with the new list (full refresh each sync).
        """
        db = self.dm.db
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            
            # Ensure table exists
            if db.db_type in ["postgresql", "postgres"]:
                raw = cursor._cursor if hasattr(cursor, '_cursor') else cursor
                raw.execute("""
                    CREATE TABLE IF NOT EXISTS player_favorites (
                        id SERIAL PRIMARY KEY,
                        championship_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        player_id TEXT NOT NULL,
                        synced_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(championship_id, user_id, player_id)
                    )
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS player_favorites (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        championship_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        player_id TEXT NOT NULL,
                        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(championship_id, user_id, player_id)
                    )
                """)
            
            # Clear existing favorites for this user+championship
            sql_del = "DELETE FROM player_favorites WHERE championship_id = ? AND user_id = ?"
            sql_del = db.adapt_params(sql_del)
            cursor.execute(sql_del, (self.championship_id, self.client.user_id or ''))
            
            # Insert new favorites
            if player_ids:
                if db.db_type in ["postgresql", "postgres"]:
                    from psycopg2.extras import execute_values
                    raw = cursor._cursor if hasattr(cursor, '_cursor') else cursor
                    values = [(self.championship_id, self.client.user_id or '', pid) for pid in player_ids]
                    execute_values(raw, """
                        INSERT INTO player_favorites (championship_id, user_id, player_id)
                        VALUES %s
                        ON CONFLICT (championship_id, user_id, player_id) DO NOTHING
                    """, values)
                else:
                    for pid in player_ids:
                        cursor.execute(
                            "INSERT OR IGNORE INTO player_favorites (championship_id, user_id, player_id) VALUES (?, ?, ?)",
                            (self.championship_id, self.client.user_id or '', pid)
                        )

    def sync_players_full(self) -> Dict:
        """Sync all players (full update - players can change basic data)
        
        Returns:
            Dict with sync results
        """
        start_time = time.time()
        logger.info("Starting full player sync...")
        
        try:
            # Get all championship players
            players_data = self.client.get_championship_players(self.championship_id)
            if not players_data or not players_data.get("players"):
                raise Exception("Could not fetch championship players")
            
            players = players_data.get("players", [])
            logger.info(f"Found {len(players)} players to sync")
            
            total_synced = 0
            stats_payload: List[Dict] = []
            player_records: List[Dict] = []
            
            for player in players:
                player_id = player.get("id")
                if not player_id:
                    continue
                
                # Collect player data for batch insert
                player_records.append({
                    "id": player_id,
                    "name": player.get("name", ""),
                    "role": player.get("role", ""),
                    "role2": player.get("role2", ""),
                    "teamId": player.get("teamId", ""),
                    "team": player.get("team", ""),
                    "slug": player.get("slug", ""),
                    "photo": player.get("photo", ""),
                    "value": player.get("value", 0),
                })
                
                clause_data = player.get("clause") or {}
                average_data = player.get("average") or {}
                owner_team_id = player.get("userteamId")
                owner_team_name = player.get("userteam")
                owner_user_id = (
                    player.get("userteamUserId")
                    or player.get("userId")
                    or owner_team_id
                )
                
                stats_payload.append({
                    "player_id": player_id,
                    "owner_team_id": owner_team_id,
                    "owner_team_name": owner_team_name,
                    "owner_user_id": owner_user_id,
                    "clause_price": clause_data.get("price"),
                    "suggested_clause": clause_data.get("suggestedClause"),
                    "average_last_five": average_data.get("averageLastFive"),
                    "average_overall": average_data.get("average")
                })
            
            # Batch insert all players in one transaction
            total_synced = self.dm.save_players_batch(player_records)
            
            if stats_payload:
                try:
                    self.dm.save_player_championship_stats(self.championship_id, stats_payload)
                except Exception as stats_err:
                    logger.warning(f"Failed to persist player championship stats: {stats_err}")
            
            # Sync favorites — store which players the user has marked as fav
            try:
                favorites = []
                for player in players:
                    if player.get("fav") is True and not player.get("userteamId"):
                        favorites.append(player.get("id"))
                self._save_favorites(favorites)
                logger.info(f"Synced {len(favorites)} favorites")
            except Exception as fav_err:
                logger.warning(f"Failed to sync favorites: {fav_err}")
            
            duration = time.time() - start_time
            status = "success"
            
            # Update sync metadata
            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="players",
                last_sync_date=datetime.now(),
                records_synced=total_synced,
                sync_duration_seconds=duration,
                sync_status=status
            )
            
            logger.info(f"Player sync complete: {total_synced} players in {duration:.2f}s")
            
            return {
                "status": status,
                "records_synced": total_synced,
                "duration_seconds": duration
            }
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Player sync failed: {e}", exc_info=True)
            
            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="players",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration
            )
            
            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration
            }
    
    def sync_match_odds(self) -> Dict:
        """Sync match odds for upcoming matches"""
        start_time = time.time()
        logger.info("Starting match odds sync...")

        try:
            odds_data = self.client.get_match_list(self.championship_id)
            if not odds_data:
                raise Exception("No match list data returned from API")

            round_info = odds_data.get("round", {}) or {}
            matches = odds_data.get("matches", []) or []
            round_id = round_info.get("_id")
            matchday = round_info.get("number")

            if not matches:
                logger.info("No matches found for odds sync")

            self.dm.save_match_odds(self.championship_id, matches, round_id=round_id, matchday=matchday)

            duration = time.time() - start_time
            status = "success"

            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="match_odds",
                last_sync_matchday=matchday,
                last_sync_date=datetime.now(),
                records_synced=len(matches),
                sync_duration_seconds=duration,
                sync_status=status
            )

            return {
                "status": status,
                "records_synced": len(matches),
                "matchday": matchday,
                "duration_seconds": duration
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Match odds sync failed: {e}", exc_info=True)

            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="match_odds",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration
            )

            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration
            }

    def sync_prizes(self) -> Dict:
        """Sync team prizes (ranking + MVP) for completed matchdays.
        
        For each closed round where all matches have status 'F':
        1. Get ranking → calculate ranking prize (flop mode)
        2. Get dreamteam → find MVP player
        3. Check all team lineups to find who had the MVP
        4. Save to team_prizes table
        """
        start_time = time.time()
        logger.info("Starting prizes sync...")

        try:
            # Get championship config for prize calculation
            from app.services.db_connection import get_db

            db = get_db()
            
            # Get config from any user's championship settings
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                sql = "SELECT money_per_ranking, mvp_bonus, ranking_mode, users_to_rank FROM user_championships WHERE championship_id = ? LIMIT 1"
                sql = db.adapt_params(sql)
                cursor.execute(sql, (self.championship_id,))
                row = cursor.fetchone()
            
            if not row:
                return {"status": "no_config", "records_synced": 0, "duration_seconds": time.time() - start_time}
            
            money_per_ranking = row[0] or 0
            mvp_bonus = row[1] or 0
            ranking_mode = row[2] or "top"
            users_to_rank = row[3] if row[3] is not None else -1

            if money_per_ranking <= 0 and mvp_bonus <= 0:
                return {"status": "no_prizes_configured", "records_synced": 0, "duration_seconds": time.time() - start_time}

            # Get teams from standings
            standings_data = self.client.get_matchday_standings(self.championship_id)
            if not standings_data:
                return {"status": "no_standings", "records_synced": 0, "duration_seconds": time.time() - start_time}

            team_list = standings_data.get("teams", standings_data.get("ranking", []))
            if not team_list:
                return {"status": "no_teams", "records_synced": 0, "duration_seconds": time.time() - start_time}

            # Get a sample userteam_id for API calls
            sample_userteam_id = team_list[0].get("teamid") or team_list[0].get("id")
            all_team_ids = []
            for t in team_list:
                tid = t.get("teamid") or t.get("id")
                if tid:
                    all_team_ids.append(tid)
            
            total_members = len(all_team_ids)

            # Get rounds
            rounds_info = self.client.get_userteam_rounds(self.championship_id, sample_userteam_id) or []
            closed_rounds = [r for r in rounds_info if r.get("status") == "closed"]

            if not closed_rounds:
                return {"status": "no_closed_rounds", "records_synced": 0, "duration_seconds": time.time() - start_time}

            # Check which rounds already have prizes synced
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                sql = "SELECT DISTINCT matchday FROM team_prizes WHERE championship_id = ?"
                sql = db.adapt_params(sql)
                cursor.execute(sql, (self.championship_id,))
                synced_matchdays = {r[0] for r in cursor.fetchall()}

            records_synced = 0
            rounds_processed = 0

            for round_info in closed_rounds:
                matchday = round_info.get("number")
                round_id = round_info.get("id") or round_info.get("_id")

                if not matchday or not round_id:
                    continue
                if matchday in synced_matchdays:
                    continue  # Already synced

                # Verify all matches are finished (status: "F")
                matches_data = self.client.get_round_matches(self.championship_id, round_id, sample_userteam_id)
                if matches_data:
                    matches = matches_data.get("matches", [])
                    if matches:
                        all_finished = all(m.get("status") == "F" for m in matches)
                        if not all_finished:
                            logger.info(f"Round {matchday} has unfinished matches (postponed), skipping prizes")
                            continue
                
                time.sleep(0.3)

                # Get ranking from DB (already synced in team_standings step)
                with db.get_connection() as conn:
                    cursor = db.get_cursor(conn)
                    sql = "SELECT team_id, position FROM team_standings WHERE championship_id = ? AND matchday = ?"
                    sql = db.adapt_params(sql)
                    cursor.execute(sql, (self.championship_id, matchday))
                    ranking_list = [{"id": row[0], "position": row[1]} for row in cursor.fetchall()]

                if not ranking_list:
                    # Fallback: fetch from API if DB doesn't have it yet
                    logger.warning(f"Round {matchday}: no ranking in DB, falling back to API")
                    ranking_data = self.client.get_round_ranking(
                        championship_id=self.championship_id,
                        round_number=matchday,
                        round_id=round_id,
                        userteam_id=sample_userteam_id
                    )
                    if isinstance(ranking_data, dict):
                        ranking_list = ranking_data.get("ranking", ranking_data.get("teams", []))
                    elif isinstance(ranking_data, list):
                        ranking_list = ranking_data
                    time.sleep(0.3)

                if not ranking_list:
                    logger.warning(f"No ranking data for round {matchday} (DB nor API)")
                    continue

                # Get dream team to find MVP
                mvp_team_id = None
                if mvp_bonus > 0:
                    dream_data = self.client.get_dream_team(self.championship_id, round_id=round_id)
                    mvp_player_id = None
                    if dream_data and isinstance(dream_data, dict):
                        mvp_player_id = dream_data.get("mvp")
                    
                    if mvp_player_id:
                        # Check each team's lineup to find who had the MVP
                        for tid in all_team_ids:
                            lineup = self.client.get_round_lineup(self.championship_id, round_id, tid)
                            if lineup:
                                lineup_ids = [p.get("id") for p in lineup]
                                if mvp_player_id in lineup_ids:
                                    mvp_team_id = tid
                                    logger.info(f"Round {matchday} MVP ({mvp_player_id}) belongs to team {tid}")
                                    break
                            time.sleep(0.2)

                # Calculate ranking prizes
                members = users_to_rank if users_to_rank > 0 else total_members
                total_pct = members * (members + 1) // 2

                prizes_to_save = []
                for entry in ranking_list:
                    team_id = entry.get("id") or entry.get("teamid")
                    position = entry.get("position", 0)
                    
                    if not team_id or not position or position > members:
                        continue

                    # Calculate ranking prize
                    if ranking_mode == "flop":
                        ratio = position / total_pct
                    else:
                        ratio = (members - position + 1) / total_pct
                    ranking_prize = round(money_per_ranking * ratio) if money_per_ranking > 0 else 0

                    # MVP prize
                    team_mvp_prize = mvp_bonus if team_id == mvp_team_id else 0

                    prizes_to_save.append((
                        self.championship_id, team_id, matchday,
                        ranking_prize, team_mvp_prize, position
                    ))

                # Save to DB
                if prizes_to_save:
                    with db.get_connection() as conn:
                        cursor = db.get_cursor(conn)
                        sql = """INSERT INTO team_prizes (championship_id, team_id, matchday, ranking_prize, mvp_prize, position, synced_at)
                                 VALUES (?, ?, ?, ?, ?, ?, NOW())
                                 ON CONFLICT (championship_id, team_id, matchday) DO UPDATE SET
                                 ranking_prize = EXCLUDED.ranking_prize, mvp_prize = EXCLUDED.mvp_prize,
                                 position = EXCLUDED.position, synced_at = NOW()"""
                        sql = db.adapt_params(sql)
                        for row in prizes_to_save:
                            cursor.execute(sql, row)
                        conn.commit()
                    
                    records_synced += len(prizes_to_save)
                    rounds_processed += 1
                    logger.info(f"Round {matchday}: saved {len(prizes_to_save)} prize records")

                time.sleep(0.3)

            duration = time.time() - start_time
            status = "success" if rounds_processed > 0 else "no_new_data"

            logger.info(f"Prizes sync complete: {rounds_processed} rounds, {records_synced} records in {duration:.2f}s")

            return {
                "status": status,
                "rounds_processed": rounds_processed,
                "records_synced": records_synced,
                "duration_seconds": duration
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Prizes sync failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "records_synced": 0,
                "duration_seconds": duration
            }

    def sync_all(self) -> Dict:
        """Run all sync operations
        
        Returns:
            Dict with results for each sync type
        """
        logger.info("=" * 60)
        logger.info("Starting full data synchronization")
        logger.info("=" * 60)
        
        # Sync players first so other syncs (transactions, rosters, etc.) have
        # the necessary player records for foreign-key constraints.
        results = {
            "players": self.sync_players_full(),
            "transactions": self.sync_transactions(),
            "clauses": self.sync_clauses(),
            "punishments_bonuses": self.sync_punishments_bonuses(),
            "dream_teams": self.sync_dream_teams_mvps(),
            "player_performance": self.sync_player_performance(),
            "rosters": self.sync_rosters(),
            "team_standings": self.sync_round_rankings(),
            "match_odds": self.sync_match_odds(),
            "prizes": self.sync_prizes(),
        }
        
        logger.info("=" * 60)
        logger.info("Full synchronization complete")
        logger.info("=" * 60)
        
        return results

