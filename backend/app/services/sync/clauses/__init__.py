"""``clauses`` sync bounded context (second extracted domain).

Extracts ``DataSyncService.sync_clauses`` into a thin DDD layering while
preserving the exact observable ``SyncResult`` payload (BR1.1, FR5):

- ``domain/ports.py``     — ``ClausesSyncDataPort`` (consumer-owned Protocol
                            describing ONLY the data operations this domain
                            consumes; no SQL, no framework — BR2.1).
- ``infrastructure/clauses_adapter.py`` — ``DataManagerClausesAdapter``, the
                            only place touching ``DataManagerV2`` (wraps the
                            existing calls verbatim — BR2.2).
- ``orchestrator.py``     — ``ClausesSyncOrchestrator``, hosting the paginated
                            ingestion (injected Futmondo client) + throttling +
                            error handling + delegation, returning the
                            SyncResult dict.

``DataSyncService.sync_clauses`` becomes a thin delegation to this orchestrator
(same signature, same return).
"""

from app.services.sync.clauses.orchestrator import ClausesSyncOrchestrator

__all__ = ["ClausesSyncOrchestrator"]
