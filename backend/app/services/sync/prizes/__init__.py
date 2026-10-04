"""``prizes`` sync bounded context (uniformised domain).

Uniformises ``DataSyncService.sync_prizes`` onto the pilot triad shape while
preserving the exact observable ``SyncResult`` payload and the typed-exception
propagation contract (BR1.1, FR5, BR2.1/2.2/2.3):

- ``domain/ports.py``     — ``PrizesSyncDataPort`` (consumer-owned Protocol; no
                            SQL, no framework — BR2.1).
- ``infrastructure/prizes_adapter.py`` — ``DataManagerPrizesAdapter``, the only
                            place touching the raw ``get_db()`` SQL (config read)
                            and the atomic ``replace_team_prizes`` writer; both
                            wrapped VERBATIM (BR2.2).
- ``orchestrator.py``     — ``PrizesSyncOrchestrator``, hosting the per-round
                            ingestion (injected Futmondo client), the
                            advanced-pseudo-round handling, the pure prize math
                            via ``prizes.calculator`` (UNCHANGED), the atomic
                            persistence, the typed-exception propagation and the
                            error handling.

The pure calculator (``prizes/calculator.py``) and the atomic writer
(``prizes/team_prizes_writer.replace_team_prizes``) are reused UNCHANGED; only
orchestration moves here.

``DataSyncService.sync_prizes`` becomes a thin delegation to this orchestrator
(same signature, same return, same raised exceptions).
"""

from app.services.sync.prizes.orchestrator import PrizesSyncOrchestrator

__all__ = ["PrizesSyncOrchestrator"]
