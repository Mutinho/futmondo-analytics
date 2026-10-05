"""Thin orchestrator for the ``clauses`` responsibility (BR1.3).

Delegates to an injected :class:`ClausesDataPort`; contains no SQL (BR1.3). Each
method preserves the exact observable behavior of the former ``DataManagerV2``
clause methods by forwarding verbatim to the adapter, which hosts the SQL and
parsing.
"""

from typing import Dict, List, Optional

from app.services.data_manager.clauses.domain.ports import ClausesDataPort


class ClausesService:
    """Coordinate clause persistence/queries over a ``ClausesDataPort``."""

    def __init__(self, port: ClausesDataPort) -> None:
        self.port = port

    def parse_clause_text(self, text: str) -> Optional[Dict[str, str]]:
        return self.port.parse_clause_text(text)

    def save_clauses(self, championship_id: str, news_items: List[Dict]) -> None:
        return self.port.save_clauses(championship_id, news_items)

    def get_user_clauses_stats(self, championship_id: str) -> Dict[str, Dict]:
        return self.port.get_user_clauses_stats(championship_id)

    def get_clauses_raw(self, championship_id: str, days: Optional[int] = None) -> List[Dict]:
        return self.port.get_clauses_raw(championship_id, days=days)

    def get_clausulable_player_stats(self, championship_id: str) -> List[Dict]:
        return self.port.get_clausulable_player_stats(championship_id)
