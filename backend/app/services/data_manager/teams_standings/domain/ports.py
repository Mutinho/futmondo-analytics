"""Consumer-owned data port for the ``teams-standings`` responsibility (BR1.3).

Structural :class:`typing.Protocol`; no SQL, no framework (BR1.3).
"""

from typing import Any, Dict, List, Optional, Protocol


class TeamsStandingsDataPort(Protocol):
    """Structural type of the surface teams-standings consumes."""

    def save_team_standing(
        self,
        championship_id: str,
        team_id: str,
        matchday: int,
        position: int,
        points: int,
        points_this_matchday: int = 0,
        team_value: Optional[int] = None,
        conn: Any = None,
        cursor: Any = None,
        **kwargs: Any,
    ) -> None:
        """Persist a team standing for a matchday."""
        ...

    def save_team(
        self,
        team_id: str,
        team_name: str,
        user_id: str = "",
        owner_name: str = "",
        current_points: int = 0,
        team_value: int = 0,
    ) -> None:
        """Persist team information."""
        ...

    def save_round_ranking(
        self, round_number: int, championship_id: str, teams: List[Dict]
    ) -> None:
        """Persist a round ranking for historical analysis."""
        ...

    def get_team_standings_history(
        self, championship_id: str, window: Optional[int] = None
    ) -> List[Dict]:
        """Return standings history per team, optionally windowed."""
        ...

    def get_latest_matchday(self, championship_id: str) -> Optional[int]:
        """Return the latest matchday available in team_standings."""
        ...

    def get_team_by_id(self, team_id: str) -> Optional[Dict]:
        """Return a team row by id, or None."""
        ...

    def get_player_streak_data(
        self, championship_id: str, min_matchday: Optional[int] = None
    ) -> List[Dict]:
        """Return player performance ordered for streak calculations."""
        ...
