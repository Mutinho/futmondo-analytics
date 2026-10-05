"""Consumer-owned data port for the ``performance`` responsibility (BR1.3).

Structural :class:`typing.Protocol`; no SQL, no framework (BR1.3). Implemented by
:class:`~app.services.data_manager.performance.infrastructure.performance_adapter.PerformanceAdapter`.
"""

from typing import Dict, List, Optional, Protocol


class PerformanceDataPort(Protocol):
    """Structural type of the persistence surface performance consumes."""

    def save_player_performance(
        self,
        championship_id: str,
        player_id: str,
        team_id: str,
        matchday: int,
        points: int,
        value: Optional[int] = None,
        was_best_player: bool = False,
        **kwargs,
    ) -> None:
        """Persist a single player-performance record."""
        ...

    def save_player_performance_batch(self, championship_id: str, records: List[Dict]) -> int:
        """Persist multiple player-performance records; return the row count."""
        ...

    def get_player_performance_history(
        self,
        championship_id: str,
        player_ids: Optional[List[str]] = None,
        window: Optional[int] = None,
    ) -> List[Dict]:
        """Return performance records filtered by players and limited matchdays."""
        ...
