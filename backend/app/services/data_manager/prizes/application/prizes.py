"""Thin orchestrator for the ``prizes`` read responsibility (BR1.3).

Delegates to an injected :class:`PrizesReadDataPort`; no SQL (BR1.3).
"""

from typing import Dict

from app.services.data_manager.prizes.domain.ports import PrizesReadDataPort


class PrizesReadService:
    """Coordinate prize reads over a ``PrizesReadDataPort``."""

    def __init__(self, port: PrizesReadDataPort) -> None:
        self.port = port

    def get_prizes_by_team(self, championship_id: str) -> Dict[str, Dict[str, int]]:
        return self.port.get_prizes_by_team(championship_id)
