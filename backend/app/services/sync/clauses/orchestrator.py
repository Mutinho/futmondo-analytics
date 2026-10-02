"""Application orchestrator for the ``clauses`` sync context (BR2.3, BR4.1).

Hosts the orchestration formerly inline in ``DataSyncService.sync_clauses``:
the paginated ingestion from the injected Futmondo client (locker-news
endpoint), the ``styp == 'clause'`` filtering and de-duplication, the stop
conditions (previously synced id, 5 consecutive empty pages, 50-page safety
limit), the ``time.sleep(0.3)`` throttling between pages, the per-page
try/except that logs and breaks, the error handling, and delegation to the
persistence port. The observable ``SyncResult`` payload is preserved
byte-for-byte (FR5.3): the same status values (``success`` when records were
synced, else ``no_new_data``; ``error`` on failure), the same keys, and the
same ``records_synced`` / ``last_sync_id`` / ``duration_seconds`` fields.

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
from app.services.sync.clauses.domain.ports import ClausesSyncDataPort
from app.services.sync.clauses.infrastructure.clauses_adapter import (
    DataManagerClausesAdapter,
)

logger = logging.getLogger(__name__)


class ClausesSyncOrchestrator:
    """Coordinate the incremental ingestion and persistence of clauses."""

    def __init__(
        self,
        client: FutmondoClient,
        championship_id: str,
        data: Optional[ClausesSyncDataPort] = None,
    ) -> None:
        """Create the orchestrator.

        Args:
            client: The Futmondo client used for ingestion (injected by the
                facade, so tests pass a fake — no network).
            championship_id: The championship whose clauses are synced.
            data: The persistence port. Defaults to the production
                ``DataManagerClausesAdapter`` to preserve historical behavior;
                tests inject a stub port.
        """
        self.client = client
        self.championship_id = championship_id
        self.data: ClausesSyncDataPort = (
            data if data is not None else DataManagerClausesAdapter()
        )

    def sync(self) -> Dict:
        """Sync clauses incrementally (equivalent to the former method).

        Returns the same observable ``SyncResult`` payload as the historical
        ``DataSyncService.sync_clauses`` (FR5): ``success`` / ``no_new_data``
        with ``records_synced`` / ``last_sync_id`` / ``duration_seconds`` on the
        happy path, or ``error`` with ``error`` / ``duration_seconds`` on
        failure.
        """
        start_time = time.time()
        logger.info("Starting incremental clause sync...")

        try:
            # Get last sync metadata
            last_sync = self.data.get_last_sync_metadata(self.championship_id, "clauses")
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
                        self.data.save_clauses(self.championship_id, clause_items)
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
            self.data.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="clauses",
                last_sync_id=final_last_id,
                last_sync_date=datetime.now(),
                records_synced=total_synced,
                sync_duration_seconds=duration,
                sync_status=status,
            )

            logger.info(f"Clause sync complete: {total_synced} records in {duration:.2f}s")

            return {
                "status": status,
                "records_synced": total_synced,
                "last_sync_id": final_last_id,
                "duration_seconds": duration,
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Clause sync failed: {e}", exc_info=True)

            self.data.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="clauses",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration,
            )

            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration,
            }
