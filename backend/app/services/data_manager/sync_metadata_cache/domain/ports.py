"""Consumer-owned data port for the ``sync-metadata-cache`` responsibility (BR1.3).

Structural :class:`typing.Protocol`; no SQL, no framework (BR1.3).
"""

from datetime import datetime
from typing import Dict, Optional, Protocol


class SyncMetadataCacheDataPort(Protocol):
    """Structural type of the surface sync-metadata-cache consumes."""

    def get_last_sync_metadata(self, championship_id: str, data_type: str) -> Optional[Dict]:
        """Return the last sync metadata for a data type, or None."""
        ...

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
        """Upsert sync metadata after a synchronization."""
        ...

    def should_update_cache(self, data_type: str) -> bool:
        """Return whether the cache should be refreshed for a data type."""
        ...
