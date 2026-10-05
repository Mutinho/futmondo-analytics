"""Thin orchestrator for the ``sync-metadata-cache`` responsibility (BR1.3).

Delegates to an injected :class:`SyncMetadataCacheDataPort`; no SQL (BR1.3).
"""

from datetime import datetime
from typing import Dict, Optional

from app.services.data_manager.sync_metadata_cache.domain.ports import (
    SyncMetadataCacheDataPort,
)


class SyncMetadataCacheService:
    """Coordinate sync metadata/cache over a ``SyncMetadataCacheDataPort``."""

    def __init__(self, port: SyncMetadataCacheDataPort) -> None:
        self.port = port

    def get_last_sync_metadata(self, championship_id: str, data_type: str) -> Optional[Dict]:
        return self.port.get_last_sync_metadata(championship_id, data_type)

    def update_sync_metadata(
        self,
        championship_id: str,
        data_type: str,
        last_sync_id: Optional[str] = None,
        last_sync_date: Optional[datetime] = None,
        last_sync_matchday: Optional[int] = None,
        records_synced: int = 0,
        sync_duration_seconds: Optional[float] = None,
        sync_status: str = "success",
        error_message: Optional[str] = None,
    ) -> None:
        return self.port.update_sync_metadata(
            championship_id,
            data_type,
            last_sync_id=last_sync_id,
            last_sync_date=last_sync_date,
            last_sync_matchday=last_sync_matchday,
            records_synced=records_synced,
            sync_duration_seconds=sync_duration_seconds,
            sync_status=sync_status,
            error_message=error_message,
        )

    def should_update_cache(self, data_type: str) -> bool:
        return self.port.should_update_cache(data_type)
