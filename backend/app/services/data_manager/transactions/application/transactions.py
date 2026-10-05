"""Thin orchestrator for the ``transactions`` responsibility (BR1.3).

Delegates to an injected :class:`TransactionsDataPort`; no SQL (BR1.3).
"""

from typing import Dict, List, Optional

from app.services.data_manager.transactions.domain.ports import TransactionsDataPort


class TransactionsService:
    """Coordinate transaction persistence/queries over a ``TransactionsDataPort``."""

    def __init__(self, port: TransactionsDataPort) -> None:
        self.port = port

    def save_player_transactions(self, player_id: str, owners_history: List[Dict]) -> None:
        return self.port.save_player_transactions(player_id, owners_history)

    def save_pressroom_transactions(self, championship_id: str, transactions: List[Dict]) -> None:
        return self.port.save_pressroom_transactions(championship_id, transactions)

    def get_all_player_transactions(self, championship_id: str) -> Dict[str, List[Dict]]:
        return self.port.get_all_player_transactions(championship_id)

    def get_user_transactions(
        self, championship_id: str, user_id: Optional[str] = None
    ) -> Dict[str, Dict]:
        return self.port.get_user_transactions(championship_id, user_id=user_id)

    def get_transactions_raw(self, championship_id: str, days: Optional[int] = None) -> List[Dict]:
        return self.port.get_transactions_raw(championship_id, days=days)
