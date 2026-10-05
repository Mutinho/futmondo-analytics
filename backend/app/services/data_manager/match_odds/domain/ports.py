"""Consumer-owned data port for the ``match-odds`` responsibility (BR1.3).

``MatchOddsDataPort`` is a structural :class:`typing.Protocol` describing ONLY
the persistence operations the match-odds orchestrator consumes. It lives in the
domain layer, imports neither ``infrastructure/`` nor any framework, and
contains no SQL (BR1.3). The application layer depends on this abstraction, not
on the concrete adapter (dependency inversion); the concrete
:class:`~app.services.data_manager.match_odds.infrastructure.match_odds_adapter.MatchOddsAdapter`
implements it.
"""

from typing import Dict, List, Optional, Protocol


class MatchOddsDataPort(Protocol):
    """Structural type of the persistence surface match-odds consumes."""

    def save_match_odds(
        self,
        championship_id: str,
        matches: List[Dict],
        round_id: Optional[str] = None,
        matchday: Optional[int] = None,
    ) -> None:
        """Persist betting odds for upcoming matches."""
        ...

    def get_match_odds(
        self,
        championship_id: str,
        matchday: Optional[int] = None,
        upcoming_only: bool = False,
    ) -> List[Dict]:
        """Retrieve stored match odds, optionally filtered by matchday/date."""
        ...
