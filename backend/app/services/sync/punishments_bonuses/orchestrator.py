"""Application orchestrator for the ``punishments_bonuses`` sync (BR2.3, BR4.1).

Hosts the orchestration formerly inline in
``DataSyncService.sync_punishments_bonuses``: the paginated ingestion from the
injected Futmondo client (locker-news endpoint), the ``styp in ['punish',
'bonus']`` filtering and de-duplication, the "no new items -> stop" condition,
the ``time.sleep(0.3)`` throttling, the 1000-page safety limit, the error
handling, and delegation to the persistence port. The observable ``SyncResult``
payload is preserved byte-for-byte (FR5.3) — including the status rule
``success if total_synced > 0 or from_id else no_new_data`` and the
``last_sync_id`` echoed from the last page's trailing item.

No credentials ever reach an exception message or log (BR4.2): the failure path
logs ``str(e)`` and stores it as ``error_message``, exactly as before.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Optional

from app.services.futmondo_client import FutmondoClient
from app.services.sync.punishments_bonuses.domain.ports import (
    PunishmentsBonusesSyncDataPort,
)
from app.services.sync.punishments_bonuses.infrastructure.punishments_bonuses_adapter import (
    DataManagerPunishmentsBonusesAdapter,
)

logger = logging.getLogger(__name__)


class PunishmentsBonusesSyncOrchestrator:
    """Coordinate the incremental ingestion and persistence of punishments/bonuses."""

    def __init__(
        self,
        client: FutmondoClient,
        championship_id: str,
        data: Optional[PunishmentsBonusesSyncDataPort] = None,
    ) -> None:
        """Create the orchestrator.

        Args:
            client: The Futmondo client used for ingestion (injected by the
                facade, so tests pass a fake — no network).
            championship_id: The championship whose punishments/bonuses are synced.
            data: The persistence port. Defaults to the production
                ``DataManagerPunishmentsBonusesAdapter``; tests inject a stub port.
        """
        self.client = client
        self.championship_id = championship_id
        self.data: PunishmentsBonusesSyncDataPort = (
            data if data is not None else DataManagerPunishmentsBonusesAdapter()
        )

    def sync(self) -> Dict:
        """Sync punishments/bonuses incrementally (equivalent to the former method)."""
        start_time = time.time()
        logger.info("Starting punishments/bonuses sync...")

        try:
            last_sync = self.data.get_last_sync_metadata(self.championship_id, "punishments_bonuses")
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

                self.data.save_punishments_bonuses(self.championship_id, punish_bonus_items)
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

            self.data.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="punishments_bonuses",
                last_sync_id=last_news_id,
                last_sync_date=datetime.now(),
                records_synced=total_synced,
                sync_duration_seconds=duration,
                sync_status=status,
            )

            logger.info(f"Punishments/bonuses sync complete: {total_synced} records in {duration:.2f}s")

            return {
                "status": status,
                "records_synced": total_synced,
                "last_sync_id": last_news_id,
                "duration_seconds": duration,
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Punishments/bonuses sync failed: {e}", exc_info=True)

            self.data.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="punishments_bonuses",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration,
            )

            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration,
            }
