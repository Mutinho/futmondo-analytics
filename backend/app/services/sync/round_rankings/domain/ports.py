"""Consumer-owned data port for the ``round_rankings`` sync (BR2.1, BR2.3).

``RoundRankingsSyncDataPort`` is a structural :class:`typing.Protocol` describing
ONLY the persistence operations the orchestrator consumes. It lives in the domain
layer, imports neither ``infrastructure/`` nor any framework, and contains no SQL
(BR2.1, BR2.2). The methods mirror the existing ``DataManagerV2`` surface
verbatim — note ``save_round_ranking`` keeps the historical ``(matchday,
championship_id, teams)`` positional order — and the adapter delegates to it
unchanged (this wave does not decompose ``data_manager`` — BR2.2).
"""

from datetime import datetime
from typing import List, Optional, Protocol


class RoundRankingsSyncDataPort(Protocol):
    """Structural type of the persistence surface the round-rankings sync consumes."""

    def save_round_ranking(
        self, matchday: int, championship_id: str, teams: List
    ) -> None:
        """Persist a matchday's team standings (delegates to DataManagerV2).

        The positional order ``(matchday, championship_id, teams)`` is the
        historical call shape and is preserved verbatim.
        """
        ...

    def get_latest_matchday(self, championship_id: str) -> Optional[int]:
        """Return the latest persisted matchday for the championship."""
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
