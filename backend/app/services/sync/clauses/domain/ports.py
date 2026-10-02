"""Consumer-owned data port for the ``clauses`` sync context (BR2.1, BR2.3).

``ClausesSyncDataPort`` is a structural :class:`typing.Protocol` describing ONLY
the persistence operations the ``clauses`` orchestrator consumes. It lives in
the domain layer, imports neither ``infrastructure/`` nor any framework, and
contains no SQL (BR2.1, BR2.2). The orchestrator depends on this abstraction,
not on the concrete ``DataManagerV2`` (dependency inversion, BR2.3); the
concrete
:class:`~app.services.sync.clauses.infrastructure.clauses_adapter.DataManagerClausesAdapter`
implements it.

All three methods mirror the existing ``DataManagerV2`` surface verbatim; the
adapter delegates to it unchanged (this wave does not decompose
``data_manager`` — BR2.2).
"""

from datetime import datetime
from typing import Dict, List, Optional, Protocol


class ClausesSyncDataPort(Protocol):
    """Structural type of the persistence surface the clauses sync consumes."""

    def get_last_sync_metadata(
        self, championship_id: str, data_type: str
    ) -> Optional[Dict]:
        """Return the last sync metadata for a data type (delegates to DataManagerV2)."""
        ...

    def save_clauses(self, championship_id: str, news_items: List[Dict]) -> None:
        """Persist the filtered clause rows (delegates to DataManagerV2)."""
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
        """Record sync metadata for a data type (delegates to DataManagerV2)."""
        ...
