"""Consumer-owned data port for the ``transactions`` responsibility (BR1.3).

Structural :class:`typing.Protocol`; no SQL, no framework (BR1.3).
"""

from typing import Dict, List, Optional, Protocol


class TransactionsDataPort(Protocol):
    """Structural type of the surface transactions consumes."""

    def save_player_transactions(self, player_id: str, owners_history: List[Dict]) -> None:
        """Legacy hook kept for compatibility with older scripts."""
        ...

    def save_pressroom_transactions(self, championship_id: str, transactions: List[Dict]) -> None:
        """Persist transactions from the pressroom endpoint (batch)."""
        ...

    def get_all_player_transactions(self, championship_id: str) -> Dict[str, List[Dict]]:
        """Return all transactions grouped by player_id."""
        ...

    def get_user_transactions(
        self, championship_id: str, user_id: Optional[str] = None
    ) -> Dict[str, Dict]:
        """Return transaction summaries grouped by user/team."""
        ...

    def get_transactions_raw(self, championship_id: str, days: Optional[int] = None) -> List[Dict]:
        """Return raw transactions, optionally limited to recent days."""
        ...
