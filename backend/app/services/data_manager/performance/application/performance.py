"""Thin orchestrator for the ``performance`` responsibility (BR1.3).

Delegates to an injected :class:`PerformanceDataPort`; contains no SQL (BR1.3).
"""

from typing import Dict, List, Optional

from app.services.data_manager.performance.domain.ports import PerformanceDataPort


class PerformanceService:
    """Coordinate performance persistence over a ``PerformanceDataPort``."""

    def __init__(self, port: PerformanceDataPort) -> None:
        self.port = port

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
        return self.port.save_player_performance(
            championship_id,
            player_id,
            team_id,
            matchday,
            points,
            value=value,
            was_best_player=was_best_player,
            **kwargs,
        )

    def save_player_performance_batch(self, championship_id: str, records: List[Dict]) -> int:
        return self.port.save_player_performance_batch(championship_id, records)

    def get_player_performance_history(
        self,
        championship_id: str,
        player_ids: Optional[List[str]] = None,
        window: Optional[int] = None,
    ) -> List[Dict]:
        return self.port.get_player_performance_history(
            championship_id, player_ids=player_ids, window=window
        )
