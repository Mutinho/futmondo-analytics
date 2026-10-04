"""Application orchestrator for the ``round_rankings`` sync (BR2.3, BR4.1).

Hosts the orchestration formerly inline in
``DataSyncService.sync_round_rankings``: the always-from-matchday-1 re-sync, the
sample-userteam discovery, the round-id mapping (with the per-matchday lazy
re-fetch), the per-matchday ranking ingestion from the injected Futmondo client,
the ``consecutive_missing >= 2`` stop, the ``max_rounds = 38`` cap, the
``time.sleep(0.2)`` throttling, the per-matchday break-on-error, the error
handling, and delegation to the persistence port. The observable ``SyncResult``
payload is preserved byte-for-byte (FR5.3) — including its distinctive keys
``rounds_synced`` / ``records_synced`` / ``last_matchday`` and the
``team_standings`` data type.

No credentials ever reach an exception message or log (BR4.2): the failure path
logs ``str(e)`` and stores it as ``error_message``, exactly as before.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Optional

from app.services.futmondo_client import FutmondoClient
from app.services.sync.round_rankings.domain.ports import RoundRankingsSyncDataPort
from app.services.sync.round_rankings.infrastructure.round_rankings_adapter import (
    DataManagerRoundRankingsAdapter,
)

logger = logging.getLogger(__name__)


class RoundRankingsSyncOrchestrator:
    """Coordinate the per-matchday ingestion and persistence of team standings."""

    def __init__(
        self,
        client: FutmondoClient,
        championship_id: str,
        data: Optional[RoundRankingsSyncDataPort] = None,
    ) -> None:
        """Create the orchestrator.

        Args:
            client: The Futmondo client used for ingestion (injected by the
                facade, so tests pass a fake — no network).
            championship_id: The championship whose standings are synced.
            data: The persistence port. Defaults to the production
                ``DataManagerRoundRankingsAdapter``; tests inject a stub port.
        """
        self.client = client
        self.championship_id = championship_id
        self.data: RoundRankingsSyncDataPort = (
            data if data is not None else DataManagerRoundRankingsAdapter()
        )

    def sync(self) -> Dict:
        """Sync team standings (round rankings) (equivalent to the former method)."""
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
                    self.data.save_round_ranking(matchday, self.championship_id, teams)
                    rounds_synced += 1
                    total_records += len(teams)

                    time.sleep(0.2)
                except Exception as round_err:
                    logger.warning(f"Failed to process standings for matchday {matchday}: {round_err}")
                    break

            current_latest = self.data.get_latest_matchday(self.championship_id) or last_matchday
            duration = time.time() - start_time
            status = "success" if rounds_synced > 0 else "no_new_data"

            self.data.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="team_standings",
                last_sync_matchday=current_latest,
                last_sync_date=datetime.now(),
                records_synced=total_records,
                sync_duration_seconds=duration,
                sync_status=status,
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
                "duration_seconds": duration,
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Team standings sync failed: {e}", exc_info=True)

            self.data.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="team_standings",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration,
            )

            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration,
            }
