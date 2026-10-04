"""Application orchestrator for the ``player_performance`` sync (BR2.3, BR4.1).

Hosts the orchestration formerly inline in
``DataSyncService.sync_player_performance``: the team-map discovery from
standings, the round-id mapping from the sample userteam, the early-return
``no_new_data`` branches (no teams / no round map) that still write metadata, the
per-matchday per-team lineup ingestion from the injected Futmondo client, the
points/value/best-player extraction with its exact fallbacks, the
``time.sleep(0.05)`` throttling, the batch save per matchday, the error handling,
and delegation to the persistence port. The observable ``SyncResult`` payload is
preserved byte-for-byte (FR5.3) — including the ``player_performance`` data type
and the ``last_sync_matchday`` key.

No credentials ever reach an exception message or log (BR4.2): the failure path
logs ``str(e)`` and stores it as ``error_message``, exactly as before.
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.services.futmondo_client import FutmondoClient
from app.services.sync.player_performance.domain.ports import (
    PlayerPerformanceSyncDataPort,
)
from app.services.sync.player_performance.infrastructure.player_performance_adapter import (
    DataManagerPlayerPerformanceAdapter,
)

logger = logging.getLogger(__name__)


class PlayerPerformanceSyncOrchestrator:
    """Coordinate the per-matchday per-team player-performance ingestion."""

    def __init__(
        self,
        client: FutmondoClient,
        championship_id: str,
        data: Optional[PlayerPerformanceSyncDataPort] = None,
    ) -> None:
        """Create the orchestrator.

        Args:
            client: The Futmondo client used for ingestion (injected by the
                facade, so tests pass a fake — no network).
            championship_id: The championship whose player performance is synced.
            data: The persistence port. Defaults to the production
                ``DataManagerPlayerPerformanceAdapter``; tests inject a stub port.
        """
        self.client = client
        self.championship_id = championship_id
        self.data: PlayerPerformanceSyncDataPort = (
            data if data is not None else DataManagerPlayerPerformanceAdapter()
        )

    def sync(self) -> Dict:
        """Sync player performance by matchday (equivalent to the former method)."""
        start_time = time.time()
        logger.info("Starting player performance sync...")

        try:
            last_sync = self.data.get_last_sync_metadata(self.championship_id, "player_performance")
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

                self.data.update_sync_metadata(
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

                self.data.update_sync_metadata(
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
                    self.data.save_player_performance_batch(self.championship_id, matchday_records)
                    total_records += len(matchday_records)
                    processed_matchday = matchday

            duration = time.time() - start_time
            status = "success" if total_records > 0 else "no_new_data"

            self.data.update_sync_metadata(
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

            self.data.update_sync_metadata(
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
