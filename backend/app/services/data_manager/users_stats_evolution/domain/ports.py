"""Consumer-owned data port for the ``users-stats-evolution`` responsibility (BR1.3).

Structural :class:`typing.Protocol`; no SQL, no framework (BR1.3). This module
owns the shared user helpers ``_ensure_user`` / ``_get_or_create_user_id`` that
earlier-extracted modules reach via the facade.
"""

from typing import Dict, List, Optional, Protocol


class UsersStatsEvolutionDataPort(Protocol):
    """Structural type of the surface users-stats-evolution consumes."""

    def get_user_id_by_name(self, user_name: str) -> Optional[Dict[str, str]]:
        """Resolve (and create if needed) user/team ids by name."""
        ...

    def get_users_unique_players_stats(self, championship_id: str) -> List[Dict]:
        """Return per-user unique-player stats aggregated with clauses/transactions."""
        ...

    def get_all_users_with_points(self, championship_id: str) -> List[Dict]:
        """Return all users/teams with their current total points."""
        ...

    def get_evolution_data_from_db(self, championship_id: str) -> Dict:
        """Return points/positions evolution per matchday per team."""
        ...

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Return a user row by id, or None."""
        ...

    def ensure_user(self, user_id: str, username: str) -> None:
        """Ensure a user row exists (owns the former ``_ensure_user`` helper)."""
        ...

    def get_or_create_user_id(self, user_id_or_username: str, username: str) -> str:
        """Resolve or create a user id (owns ``_get_or_create_user_id``)."""
        ...
