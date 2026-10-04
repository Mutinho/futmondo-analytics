"""``rosters`` sync bounded context (extracted domain).

Extracts ``DataSyncService.sync_rosters`` into a thin DDD layering while
preserving the exact observable ``SyncResult`` payload (BR1.1, FR5):

- ``domain/ports.py``     — ``RostersSyncDataPort`` (consumer-owned Protocol;
                            no SQL, no framework — BR2.1).
- ``infrastructure/rosters_adapter.py`` — ``DataManagerRostersAdapter``, the
                            only place touching ``DataManagerV2`` (wraps calls
                            verbatim — BR2.2).
- ``orchestrator.py``     — ``RostersSyncOrchestrator``, hosting the round/team
                            discovery, ingestion (injected Futmondo client),
                            throttling, error handling and delegation.

``_find_championship`` STAYS in ``DataSyncService`` and is injected into the
orchestrator as a callable (``find_championship``), so it is not duplicated.

``DataSyncService.sync_rosters`` becomes a thin delegation to this orchestrator
(same signature, same return).
"""

from app.services.sync.rosters.orchestrator import RostersSyncOrchestrator

__all__ = ["RostersSyncOrchestrator"]
