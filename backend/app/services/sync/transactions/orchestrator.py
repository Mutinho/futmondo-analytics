"""Application orchestrator for the ``transactions`` sync context (BR2.3, BR4.1).

Hosts the orchestration formerly inline in ``DataSyncService.sync_transactions``:
the idempotent column-ALTER call, the paginated ingestion from the injected
Futmondo client (pressroom endpoint), the transaction filtering and
de-duplication, the stop conditions (previously synced id, empty page, no-new-
transactions-this-page, 50-page safety limit), the ``time.sleep(0.3)`` throttling
between pages, the per-page try/except that logs and breaks, the market-value
enrichment, the error handling, and delegation to the persistence port. The
observable ``SyncResult`` payload is preserved byte-for-byte (FR5.3).

The market-value enrichment preserves its observable throttle EXACTLY (R-01):
``time.sleep(0.5)`` after each fullprofile API call AND ``time.sleep(5)`` after
every batch of 20 fetched profiles, with per-player caching so a repeated
``player_id`` costs neither a second call nor a second sleep. The pure
date-matching is delegated to
:func:`~app.services.sync.transactions.domain.pricing.find_price_at_date`.

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
from app.services.sync.transactions.domain.ports import TransactionsSyncDataPort
from app.services.sync.transactions.domain.pricing import find_price_at_date
from app.services.sync.transactions.infrastructure.transactions_adapter import (
    DataManagerTransactionsAdapter,
)

logger = logging.getLogger(__name__)


class TransactionsSyncOrchestrator:
    """Coordinate the incremental ingestion, persistence and enrichment of transactions."""

    def __init__(
        self,
        client: FutmondoClient,
        championship_id: str,
        data: Optional[TransactionsSyncDataPort] = None,
    ) -> None:
        """Create the orchestrator.

        Args:
            client: The Futmondo client used for ingestion/enrichment (injected
                by the facade, so tests pass a fake — no network).
            championship_id: The championship whose transactions are synced.
            data: The persistence port. Defaults to the production
                ``DataManagerTransactionsAdapter`` to preserve historical
                behavior; tests inject a stub port.
        """
        self.client = client
        self.championship_id = championship_id
        self.data: TransactionsSyncDataPort = (
            data if data is not None else DataManagerTransactionsAdapter()
        )

    def _enrich_market_values(self) -> int:
        """Fill market_value_at_purchase for pending transactions (equivalent).

        Preserves the historical throttle EXACTLY (R-01): 0.5s after each API
        call and 5s after each batch of 20 fetched profiles, with per-player
        caching. The SQL lifecycle lives in the adapter; the per-row value
        computation (client fetch + throttle + pure pricing) is this callback.
        """
        # Cache fullprofiles to avoid duplicate calls for same player
        profile_cache: Dict = {}
        batch_count = {"n": 0}

        def resolve_market_value(player_id, txn_date, is_market_purchase):
            # Get or fetch profile
            if player_id not in profile_cache:
                profile = self.client.get_player_fullprofile(player_id)
                profile_cache[player_id] = profile
                batch_count["n"] += 1
                time.sleep(0.5)  # Rate limiting — 500ms between API calls

                # Pause between batches of 20 to avoid detection
                if batch_count["n"] % 20 == 0:
                    logger.info(f"  Enriched batch ({batch_count['n']} profiles fetched), pausing 5s...")
                    time.sleep(5)
            else:
                profile = profile_cache[player_id]

            if not profile or "prices" not in profile:
                return None

            prices = profile["prices"]
            if not prices:
                return None

            # Find price closest to transaction date
            return find_price_at_date(
                prices, txn_date, prefer_previous_day=is_market_purchase
            )

        return self.data.enrich_market_values(self.championship_id, resolve_market_value)

    def sync(self) -> Dict:
        """Sync transactions incrementally (equivalent to the former method).

        Returns the same observable ``SyncResult`` payload as the historical
        ``DataSyncService.sync_transactions`` (FR5): ``success`` / ``no_new_data``
        with ``records_synced`` / ``last_sync_id`` / ``duration_seconds`` on the
        happy path, or ``error`` with ``error`` / ``duration_seconds`` on failure.
        """
        start_time = time.time()
        logger.info("Starting incremental transaction sync...")

        # Ensure market_value_at_purchase and bids_json columns exist
        self.data.ensure_transaction_columns()

        try:
            # Get last sync metadata
            last_sync = self.data.get_last_sync_metadata(self.championship_id, "transactions")
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
                        self.data.save_pressroom_transactions(self.championship_id, transaction_items)
                        total_synced += len(transaction_items)
                        logger.info(f"📰 Page {page_count}: Saved {len(transaction_items)} transactions (total: {total_synced})")

                        # Store bids data for transactions that have them
                        self.data.store_bids(transaction_items)

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
            self.data.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="transactions",
                last_sync_id=last_transaction_id,
                last_sync_date=datetime.now(),
                records_synced=total_synced,
                sync_duration_seconds=duration,
                sync_status=status,
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
                "duration_seconds": duration,
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Transaction sync failed: {e}", exc_info=True)

            self.data.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="transactions",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration,
            )

            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration,
            }
