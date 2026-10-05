"""Thin orchestrator for the ``players`` responsibility (BR1.3).

Delegates to an injected :class:`PlayersDataPort`; no SQL (BR1.3).
"""

from typing import Dict, List, Optional

from app.services.data_manager.players.domain.ports import PlayersDataPort


class PlayersService:
    """Coordinate player persistence/queries over a ``PlayersDataPort``."""

    def __init__(self, port: PlayersDataPort) -> None:
        self.port = port

    def save_player(self, player_data: Dict) -> Optional[str]:
        return self.port.save_player(player_data)

    def save_players_batch(self, players: List[Dict]) -> int:
        return self.port.save_players_batch(players)

    def save_players(self, players: List[Dict]) -> None:
        return self.port.save_players(players)

    def delete_orphan_players(self, live_player_ids: List[str]) -> int:
        return self.port.delete_orphan_players(live_player_ids)

    def get_all_players_with_points(self, championship_id: str) -> List[Dict]:
        return self.port.get_all_players_with_points(championship_id)

    def get_player_by_id(self, player_id: str) -> Optional[Dict]:
        return self.port.get_player_by_id(player_id)

    def save_player_championship_stats(
        self, championship_id: str, player_stats: List[Dict]
    ) -> None:
        return self.port.save_player_championship_stats(championship_id, player_stats)
