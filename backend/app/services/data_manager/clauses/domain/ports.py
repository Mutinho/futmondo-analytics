"""Consumer-owned data port for the ``clauses`` responsibility (BR1.3).

``ClausesDataPort`` is a structural :class:`typing.Protocol` describing ONLY the
operations the clauses orchestrator consumes. It lives in the domain layer,
imports neither ``infrastructure/`` nor any framework, and contains no SQL
(BR1.3). The application layer depends on this abstraction, not on the concrete
adapter (dependency inversion).
"""

from typing import Dict, List, Optional, Protocol


class ClausesDataPort(Protocol):
    """Structural type of the persistence surface clauses consumes."""

    def parse_clause_text(self, text: str) -> Optional[Dict[str, str]]:
        """Parse clause HTML text into payer/receiver/amount/player fields."""
        ...

    def save_clauses(self, championship_id: str, news_items: List[Dict]) -> None:
        """Persist clauses parsed from locker-room news items."""
        ...

    def get_user_clauses_stats(self, championship_id: str) -> Dict[str, Dict]:
        """Aggregate clause statistics grouped by user/team."""
        ...

    def get_clauses_raw(self, championship_id: str, days: Optional[int] = None) -> List[Dict]:
        """Return raw clause payments, optionally limited to recent days."""
        ...

    def get_clausulable_player_stats(self, championship_id: str) -> List[Dict]:
        """Return stored clause metrics for clausulable player ranking."""
        ...
