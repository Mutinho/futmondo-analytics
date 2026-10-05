"""Thin orchestrator for the ``match-odds`` responsibility (BR1.3).

Delegates to an injected :class:`MatchOddsDataPort`; contains no SQL (BR1.3).
The two methods preserve the exact observable behavior of the former
``DataManagerV2.save_match_odds`` / ``get_match_odds`` by forwarding verbatim to
the adapter, which hosts the SQL.
"""

from typing import Dict, List, Optional

from app.services.data_manager.match_odds.domain.ports import MatchOddsDataPort


class MatchOddsService:
    """Coordinate match-odds persistence over a ``MatchOddsDataPort``."""

    def __init__(self, port: MatchOddsDataPort) -> None:
        self.port = port

    def save_match_odds(
        self,
        championship_id: str,
        matches: List[Dict],
        round_id: Optional[str] = None,
        matchday: Optional[int] = None,
    ) -> None:
        return self.port.save_match_odds(
            championship_id, matches, round_id=round_id, matchday=matchday
        )

    def get_match_odds(
        self,
        championship_id: str,
        matchday: Optional[int] = None,
        upcoming_only: bool = False,
    ) -> List[Dict]:
        return self.port.get_match_odds(
            championship_id, matchday=matchday, upcoming_only=upcoming_only
        )
