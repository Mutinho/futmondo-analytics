"""``transactions`` sync bounded context (extracted domain).

Extracts ``DataSyncService.sync_transactions`` into a thin DDD layering while
preserving the exact observable ``SyncResult`` payload (BR1.1, FR5):

- ``domain/ports.py``     — ``TransactionsSyncDataPort`` (consumer-owned
                            Protocol describing ONLY the data operations this
                            domain consumes; no SQL, no framework — BR2.1).
- ``domain/pricing.py``   — ``find_price_at_date``, the pure price-matching
                            helper (no I/O), extracted from the former private
                            ``_find_price_at_date``.
- ``infrastructure/transactions_adapter.py`` — ``DataManagerTransactionsAdapter``,
                            the only place touching ``DataManagerV2`` (wraps the
                            existing calls and the raw SQL verbatim — BR2.2).
- ``orchestrator.py``     — ``TransactionsSyncOrchestrator``, hosting the
                            paginated ingestion (injected Futmondo client), the
                            throttling, the market-value enrichment with its
                            0.5s-per-call / 5s-per-batch-of-20 cadence, the error
                            handling, and delegation to the persistence port.

``DataSyncService.sync_transactions`` becomes a thin delegation to this
orchestrator (same signature, same return).
"""

from app.services.sync.transactions.orchestrator import TransactionsSyncOrchestrator

__all__ = ["TransactionsSyncOrchestrator"]
