"""``player_performance`` sync bounded context (extracted domain).

Extracts ``DataSyncService.sync_player_performance`` into a thin DDD layering
while preserving the exact observable ``SyncResult`` payload (BR1.1, FR5):

- ``domain/ports.py``     — ``PlayerPerformanceSyncDataPort`` (consumer-owned
                            Protocol; no SQL, no framework — BR2.1).
- ``infrastructure/player_performance_adapter.py`` —
                            ``DataManagerPlayerPerformanceAdapter``, the only
                            place touching ``DataManagerV2`` (wraps calls
                            verbatim — BR2.2).
- ``orchestrator.py``     — ``PlayerPerformanceSyncOrchestrator``, hosting the
                            team/round discovery, per-matchday per-team lineup
                            ingestion (injected Futmondo client), the point/value
                            extraction, throttling, error handling and delegation.

``DataSyncService.sync_player_performance`` becomes a thin delegation to this
orchestrator (same signature, same return).
"""

from app.services.sync.player_performance.orchestrator import (
    PlayerPerformanceSyncOrchestrator,
)

__all__ = ["PlayerPerformanceSyncOrchestrator"]
