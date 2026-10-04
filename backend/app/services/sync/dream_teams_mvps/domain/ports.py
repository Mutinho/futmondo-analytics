"""Consumer-owned data port for the ``dream_teams_mvps`` sync (BR2.1, BR2.3).

``DreamTeamsMvpsSyncDataPort`` is a structural :class:`typing.Protocol` describing
ONLY the persistence operations the orchestrator consumes. It lives in the domain
layer, imports neither ``infrastructure/`` nor any framework, and contains no SQL
(BR2.1, BR2.2). The three methods mirror the existing ``DataManagerV2`` surface
verbatim; the adapter delegates to it unchanged (this wave does not decompose
``data_manager`` — BR2.2).
"""

from datetime import datetime
from typing import Dict, List, Optional, Protocol


class DreamTeamsMvpsSyncDataPort(Protocol):
    """Structural type of the persistence surface the dream-teams sync consumes."""

    def get_last_sync_metadata(
        self, championship_id: str, data_type: str
    ) -> Optional[Dict]:
        """Return the last sync metadata for a data type (delegates to DataManagerV2)."""
        ...

    def save_dream_team_mvp(
        self,
        championship_id: str,
        round_id: str,
        matchday: int,
        dream_team_players: List,
        mvp_id,
        player_details: Optional[Dict] = None,
    ) -> None:
        """Persist a round's dream team + MVP (delegates to DataManagerV2)."""
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
