"""``punishments_bonuses`` sync bounded context (extracted domain).

Extracts ``DataSyncService.sync_punishments_bonuses`` into a thin DDD layering
while preserving the exact observable ``SyncResult`` payload (BR1.1, FR5):

- ``domain/ports.py``     — ``PunishmentsBonusesSyncDataPort`` (consumer-owned
                            Protocol; no SQL, no framework — BR2.1).
- ``infrastructure/punishments_bonuses_adapter.py`` —
                            ``DataManagerPunishmentsBonusesAdapter``, the only
                            place touching ``DataManagerV2`` (wraps the existing
                            calls verbatim — BR2.2).
- ``orchestrator.py``     — ``PunishmentsBonusesSyncOrchestrator``, hosting the
                            paginated ingestion (injected Futmondo client),
                            throttling, error handling and delegation.

``DataSyncService.sync_punishments_bonuses`` becomes a thin delegation to this
orchestrator (same signature, same return).
"""

from app.services.sync.punishments_bonuses.orchestrator import (
    PunishmentsBonusesSyncOrchestrator,
)

__all__ = ["PunishmentsBonusesSyncOrchestrator"]
