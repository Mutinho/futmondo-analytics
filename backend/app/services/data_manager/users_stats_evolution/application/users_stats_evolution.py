"""Thin orchestrator for the ``users-stats-evolution`` responsibility (BR1.3).

Delegates to an injected :class:`UsersStatsEvolutionDataPort`; no SQL (BR1.3).
Owns the shared user helpers (``ensure_user`` / ``get_or_create_user_id``) that
the facade exposes under their original private names for other modules.
"""

from typing import Dict, List, Optional

from app.services.data_manager.users_stats_evolution.domain.ports import (
    UsersStatsEvolutionDataPort,
)


class UsersStatsEvolutionService:
    """Coordinate user stats/evolution over a ``UsersStatsEvolutionDataPort``."""

    def __init__(self, port: UsersStatsEvolutionDataPort) -> None:
        self.port = port

    def get_user_id_by_name(self, user_name: str) -> Optional[Dict[str, str]]:
        return self.port.get_user_id_by_name(user_name)

    def get_users_unique_players_stats(self, championship_id: str) -> List[Dict]:
        return self.port.get_users_unique_players_stats(championship_id)

    def get_all_users_with_points(self, championship_id: str) -> List[Dict]:
        return self.port.get_all_users_with_points(championship_id)

    def get_evolution_data_from_db(self, championship_id: str) -> Dict:
        return self.port.get_evolution_data_from_db(championship_id)

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        return self.port.get_user_by_id(user_id)

    def ensure_user(self, user_id: str, username: str) -> None:
        return self.port.ensure_user(user_id, username)

    def get_or_create_user_id(self, user_id_or_username: str, username: str) -> str:
        return self.port.get_or_create_user_id(user_id_or_username, username)
