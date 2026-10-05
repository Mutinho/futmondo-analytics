"""Consumer-owned data port for the ``market-roster`` responsibility (BR1.3).

Structural :class:`typing.Protocol`; no SQL, no framework (BR1.3).
"""

from typing import Dict, List, Optional, Protocol


class MarketRosterDataPort(Protocol):
    """Structural type of the surface market-roster consumes."""

    def save_market_players(
        self, championship_id: str, players: List[Dict], matchday: Optional[int] = None
    ) -> None:
        """Persist market players with historical tracking."""
        ...

    def save_team_roster(
        self,
        championship_id: str,
        team_id: str,
        players: List[Dict],
        matchday: Optional[int] = None,
    ) -> None:
        """Persist a team roster with historical tracking."""
        ...

    def get_free_agent_candidates(self, championship_id: str) -> List[Dict]:
        """Return players without owner from player_championship_stats."""
        ...
