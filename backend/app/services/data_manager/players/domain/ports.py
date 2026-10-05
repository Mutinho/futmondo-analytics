"""Consumer-owned data port for the ``players`` responsibility (BR1.3).

Structural :class:`typing.Protocol`; no SQL, no framework (BR1.3).
"""

from typing import Dict, List, Optional, Protocol


class PlayersDataPort(Protocol):
    """Structural type of the surface players consumes."""

    def save_player(self, player_data: Dict) -> Optional[str]:
        """Persist/update a single player, returning its id or None."""
        ...

    def save_players_batch(self, players: List[Dict]) -> int:
        """Batch upsert players, returning the count processed."""
        ...

    def save_players(self, players: List[Dict]) -> None:
        """Persist players with photo-URL derivation."""
        ...

    def delete_orphan_players(self, live_player_ids: List[str]) -> int:
        """Delete players absent from the API list and all history tables."""
        ...

    def get_all_players_with_points(self, championship_id: str) -> List[Dict]:
        """Return all players with their total points."""
        ...

    def get_player_by_id(self, player_id: str) -> Optional[Dict]:
        """Return a player row by id, or None."""
        ...

    def save_player_championship_stats(
        self, championship_id: str, player_stats: List[Dict]
    ) -> None:
        """Persist clause/average metrics for players in a championship (batch)."""
        ...
