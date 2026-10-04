"""``players_full`` sync bounded context (extracted domain).

Extracts ``DataSyncService.sync_players_full`` into a thin DDD layering while
preserving the exact observable ``SyncResult`` payload (BR1.1, FR5):

- ``domain/ports.py``     — ``PlayersFullSyncDataPort`` (consumer-owned Protocol;
                            no SQL, no framework — BR2.1).
- ``infrastructure/players_full_adapter.py`` — ``DataManagerPlayersFullAdapter``,
                            the only place touching ``DataManagerV2`` and its raw
                            ``db`` (wraps calls and the ``_save_favorites`` raw
                            SQL — including the Postgres ``execute_values`` branch
                            — verbatim; BR2.2).
- ``orchestrator.py``     — ``PlayersFullSyncOrchestrator``, hosting the
                            ingestion (injected Futmondo client), the record/stat
                            payload assembly, the orphan cleanup, the favorites
                            selection, the error handling and delegation.

``DataSyncService.sync_players_full`` becomes a thin delegation to this
orchestrator (same signature, same return). The orchestrator routes its result
under the ``players`` key in ``sync_all`` (name-key divergence, unchanged).
"""

from app.services.sync.players_full.orchestrator import PlayersFullSyncOrchestrator

__all__ = ["PlayersFullSyncOrchestrator"]
