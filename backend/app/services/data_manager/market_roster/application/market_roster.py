"""Thin orchestrator for the ``market-roster`` responsibility (BR1.3).

Delegates to an injected :class:`MarketRosterDataPort`; no SQL (BR1.3).
"""

from typing import Dict, List, Optional

from app.services.data_manager.market_roster.domain.ports import MarketRosterDataPort


class MarketRosterService:
    """Coordinate market/roster persistence over a ``MarketRosterDataPort``."""

    def __init__(self, port: MarketRosterDataPort) -> None:
        self.port = port

    def save_market_players(
        self, championship_id: str, players: List[Dict], matchday: Optional[int] = None
    ) -> None:
        return self.port.save_market_players(championship_id, players, matchday=matchday)

    def save_team_roster(
        self,
        championship_id: str,
        team_id: str,
        players: List[Dict],
        matchday: Optional[int] = None,
    ) -> None:
        return self.port.save_team_roster(championship_id, team_id, players, matchday=matchday)

    def get_free_agent_candidates(self, championship_id: str) -> List[Dict]:
        return self.port.get_free_agent_candidates(championship_id)
