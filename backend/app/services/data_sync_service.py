"""
Data Sync Service - Handles incremental and full data synchronization
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
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
        
        try:
            # Get last sync metadata
            last_sync = self.dm.get_last_sync_metadata(self.championship_id, "transactions")
            from_id = last_sync.get("last_sync_id", "") if last_sync else ""
            
            logger.info(f"Last sync ID: {from_id or 'None (full sync)'}")
            
            total_synced = 0
            page_count = 0
            seen_ids = set()
            last_transaction_id = from_id
            
            while True:
                try:
                    page_count += 1
                    logger.info(f"Fetching pressroom page {page_count}...")
                    
                    pressroom_data = self.client.get_pressroom_news(self.championship_id, from_id=from_id)
                    if not pressroom_data:
                        break
                    
                    news_items = pressroom_data.get("news", pressroom_data.get("data", []))
                    if not news_items:
                        break
                    
                    # Filter transactions (have _player, _buyer, or _seller)
                    transaction_items = []
                    for item in news_items:
                        if item.get("_player") or item.get("_buyer") or item.get("_seller"):
                            transaction_id = item.get("_id")
                            if transaction_id and transaction_id not in seen_ids:
                                seen_ids.add(transaction_id)
                                transaction_items.append(item)
                    
                    if len(transaction_items) == 0:
                        logger.info("No new transactions, stopping")
                        break
                    
                    # Save transactions
                    self.dm.save_pressroom_transactions(self.championship_id, transaction_items)
                    total_synced += len(transaction_items)
                    
                    # Get last transaction ID for next page
                    last_item = news_items[-1]
                    last_transaction_id = last_item.get("_id", "")
                    from_id = last_transaction_id
                    
                    time.sleep(0.3)  # Rate limiting
                    
                    if page_count >= 1000:  # Safety limit
                        logger.warning("Page limit reached (1000)")
                        break
                        
                except Exception as e:
                    logger.error(f"Error fetching pressroom page {page_count}: {e}")
                    break
            
            duration = time.time() - start_time
            status = "success" if total_synced > 0 or from_id else "no_new_data"
            
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
            from_id = last_sync.get("last_sync_id", "") if last_sync else ""
            
            logger.info(f"Last sync ID: {from_id or 'None (full sync)'}")
            
            total_synced = 0
            page_count = 0
            seen_ids = set()
            last_news_id = from_id
            
            while True:
                try:
                    page_count += 1
                    logger.info(f"Fetching locker news page {page_count}...")
                    
                    locker_news_data = self.client.get_locker_news(self.championship_id, from_id=from_id)
                    if not locker_news_data:
                        break
                    
                    news_items = locker_news_data.get("news", locker_news_data.get("data", []))
                    if not news_items:
                        break
                    
                    # Filter only clause items
                    clause_items = []
                    for item in news_items:
                        if item.get("styp") == "clause":
                            news_id = item.get("_id")
                            if news_id and news_id not in seen_ids:
                                seen_ids.add(news_id)
                                clause_items.append(item)
                    
                    if len(clause_items) == 0:
                        logger.info("No new clauses, stopping")
                        break
                    
                    # Save clauses
                    self.dm.save_clauses(self.championship_id, clause_items)
                    total_synced += len(clause_items)
                    
                    # Get last news ID for next page
                    last_item = news_items[-1]
                    last_news_id = last_item.get("_id", "")
                    from_id = last_news_id
                    
                    time.sleep(0.3)  # Rate limiting
                    
                    if page_count >= 1000:  # Safety limit
                        logger.warning("Page limit reached (1000)")
                        break
                        
                except Exception as e:
                    logger.error(f"Error fetching locker news page {page_count}: {e}")
                    break
            
            duration = time.time() - start_time
            status = "success" if total_synced > 0 or from_id else "no_new_data"
            
            # Update sync metadata
            self.dm.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="clauses",
                last_sync_id=last_news_id,
                last_sync_date=datetime.now(),
                records_synced=total_synced,
                sync_duration_seconds=duration,
                sync_status=status
            )
            
            logger.info(f"Clause sync complete: {total_synced} records in {duration:.2f}s")
            
            return {
                "status": status,
                "records_synced": total_synced,
                "last_sync_id": last_news_id,
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
            
            for player in players:
                try:
                    player_id = player.get("id")
                    if not player_id:
                        continue
                    
                    # Save player (will update if exists)
                    self.dm.save_player({
                        "id": player_id,
                        "name": player.get("name", ""),
                        "role": player.get("role", ""),
                        "real_team_id": player.get("teamId", ""),
                        "real_team_name": player.get("team", ""),
                        "slug": player.get("slug", ""),
                        "photo_url": player.get("photo", "")
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
                    
                    total_synced += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to save player {player.get('id')}: {e}")
                    continue
            
            if stats_payload:
                try:
                    self.dm.save_player_championship_stats(self.championship_id, stats_payload)
                except Exception as stats_err:
                    logger.warning(f"Failed to persist player championship stats: {stats_err}")
            
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
            "rosters": self.sync_rosters()
        }
        
        logger.info("=" * 60)
        logger.info("Full synchronization complete")
        logger.info("=" * 60)
        
        return results

