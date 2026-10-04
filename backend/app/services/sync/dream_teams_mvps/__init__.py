"""``dream_teams_mvps`` sync bounded context (extracted domain).

Extracts ``DataSyncService.sync_dream_teams_mvps`` into a thin DDD layering while
preserving the exact observable ``SyncResult`` payload (BR1.1, FR5):

- ``domain/ports.py``     — ``DreamTeamsMvpsSyncDataPort`` (consumer-owned
                            Protocol; no SQL, no framework — BR2.1).
- ``infrastructure/dream_teams_mvps_adapter.py`` —
                            ``DataManagerDreamTeamsMvpsAdapter``, the only place
                            touching ``DataManagerV2`` (wraps calls verbatim —
                            BR2.2).
- ``orchestrator.py``     — ``DreamTeamsMvpsSyncOrchestrator``, hosting the
                            round discovery, ingestion (injected Futmondo
                            client), throttling, error handling and delegation.

``_find_championship`` STAYS in ``DataSyncService`` and is injected into the
orchestrator as a callable (``find_championship``), so it is not duplicated.

``DataSyncService.sync_dream_teams_mvps`` becomes a thin delegation to this
orchestrator (same signature, same return).
"""

from app.services.sync.dream_teams_mvps.orchestrator import (
    DreamTeamsMvpsSyncOrchestrator,
)

__all__ = ["DreamTeamsMvpsSyncOrchestrator"]
