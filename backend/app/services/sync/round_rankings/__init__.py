"""``round_rankings`` sync bounded context (extracted domain).

Extracts ``DataSyncService.sync_round_rankings`` into a thin DDD layering while
preserving the exact observable ``SyncResult`` payload (BR1.1, FR5) — including
its distinctive keys ``rounds_synced`` / ``records_synced`` / ``last_matchday``
and its ``team_standings`` data type:

- ``domain/ports.py``     — ``RoundRankingsSyncDataPort`` (consumer-owned
                            Protocol; no SQL, no framework — BR2.1).
- ``infrastructure/round_rankings_adapter.py`` —
                            ``DataManagerRoundRankingsAdapter``, the only place
                            touching ``DataManagerV2`` (wraps calls verbatim —
                            BR2.2).
- ``orchestrator.py``     — ``RoundRankingsSyncOrchestrator``, hosting the round
                            discovery, per-matchday ingestion (injected Futmondo
                            client), throttling, the consecutive-miss stop, the
                            error handling and delegation.

``DataSyncService.sync_round_rankings`` becomes a thin delegation to this
orchestrator (same signature, same return).
"""

from app.services.sync.round_rankings.orchestrator import RoundRankingsSyncOrchestrator

__all__ = ["RoundRankingsSyncOrchestrator"]
