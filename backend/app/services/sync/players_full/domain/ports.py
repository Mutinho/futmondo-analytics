"""Consumer-owned data port for the ``players_full`` sync (BR2.1, BR2.3).

``PlayersFullSyncDataPort`` is a structural :class:`typing.Protocol` describing
ONLY the persistence operations the orchestrator consumes. It lives in the domain
layer, imports neither ``infrastructure/`` nor any framework, and contains no SQL
(BR2.1, BR2.2). Most methods mirror the existing ``DataManagerV2`` surface
verbatim; ``save_favorites`` wraps the raw SQL that used to run inline on
``self.dm.db`` (including the Postgres ``execute_values`` branch), moved VERBATIM
into the adapter — never into ``data_manager_v2.py`` and never rewritten.
"""

from datetime import datetime
from typing import Dict, List, Optional, Protocol


class PlayersFullSyncDataPort(Protocol):
    """Structural type of the persistence surface the players-full sync consumes."""

    def save_players_batch(self, player_records: List[Dict]) -> int:
        """Upsert all player rows in one transaction; return the synced count."""
        ...

    def delete_orphan_players(self, live_ids: List[str]) -> int:
        """Remove players absent from the live list AND with no history; return count."""
        ...

    def save_player_championship_stats(
        self, championship_id: str, stats_payload: List[Dict]
    ) -> None:
        """Persist per-championship player stats (delegates to DataManagerV2)."""
        ...

    def save_favorites(
        self, championship_id: str, user_id: str, player_ids: List[str]
    ) -> None:
        """Replace the user's favorite player ids for the championship.

        Wraps the raw SQL formerly inline in ``_save_favorites`` (table ensure,
        delete-then-insert, Postgres ``execute_values`` branch) VERBATIM.
        """
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
