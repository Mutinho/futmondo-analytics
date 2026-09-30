"""Application orchestrator for the ``match_odds`` sync context (BR2.3, BR4.1).

Hosts the orchestration formerly inline in ``DataSyncService.sync_match_odds``:
ingestion from the injected Futmondo client, the timing/throttling behavior, the
error handling, and delegation to the persistence port. The observable
``SyncResult`` payload is preserved byte-for-byte (FR5.3): the same status
values, the same keys, and the same ``records_synced`` / ``matchday`` /
``duration_seconds`` fields.

No credentials ever reach an exception message or log (BR4.2): the failure path
logs ``str(e)`` of the caught error and stores it as ``error_message``, exactly
as the former inline code did — the Futmondo client already keeps credentials
out of its own errors.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Optional

from app.services.futmondo_client import FutmondoClient
from app.services.sync.match_odds.domain.ports import MatchOddsSyncDataPort
from app.services.sync.match_odds.infrastructure.match_odds_adapter import (
    DataManagerMatchOddsAdapter,
)

logger = logging.getLogger(__name__)


class MatchOddsSyncOrchestrator:
    """Coordinate the ingestion and persistence of upcoming-match odds."""

    def __init__(
        self,
        client: FutmondoClient,
        championship_id: str,
        data: Optional[MatchOddsSyncDataPort] = None,
    ) -> None:
        """Create the orchestrator.

        Args:
            client: The Futmondo client used for ingestion (injected by the
                facade, so tests pass a fake — no network).
            championship_id: The championship whose match odds are synced.
            data: The persistence port. Defaults to the production
                ``DataManagerMatchOddsAdapter`` to preserve historical behavior;
                tests inject a stub port.
        """
        self.client = client
        self.championship_id = championship_id
        self.data: MatchOddsSyncDataPort = (
            data if data is not None else DataManagerMatchOddsAdapter()
        )

    def sync(self) -> Dict:
        """Sync match odds for upcoming matches (equivalent to the former method).

        Returns the same observable ``SyncResult`` payload as the historical
        ``DataSyncService.sync_match_odds`` (FR5): ``success`` with
        ``records_synced`` / ``matchday`` / ``duration_seconds`` on the happy
        path, or ``error`` with ``error`` / ``duration_seconds`` on failure.
        """
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

            self.data.save_match_odds(
                self.championship_id, matches, round_id=round_id, matchday=matchday
            )

            duration = time.time() - start_time
            status = "success"

            self.data.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="match_odds",
                last_sync_matchday=matchday,
                last_sync_date=datetime.now(),
                records_synced=len(matches),
                sync_duration_seconds=duration,
                sync_status=status,
            )

            return {
                "status": status,
                "records_synced": len(matches),
                "matchday": matchday,
                "duration_seconds": duration,
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Match odds sync failed: {e}", exc_info=True)

            self.data.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="match_odds",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration,
            )

            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration,
            }
