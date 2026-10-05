"""Thin orchestrator for the ``teams-standings`` responsibility (BR1.3).

Delegates to an injected :class:`TeamsStandingsDataPort`; no SQL (BR1.3).
"""

from typing import Any, Dict, List, Optional

from app.services.data_manager.teams_standings.domain.ports import TeamsStandingsDataPort


class TeamsStandingsService:
    """Coordinate standings persistence/queries over a ``TeamsStandingsDataPort``."""

    def __init__(self, port: TeamsStandingsDataPort) -> None:
        self.port = port

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
        return self.port.save_team_standing(
            championship_id,
            team_id,
            matchday,
            position,
            points,
            points_this_matchday=points_this_matchday,
            team_value=team_value,
            conn=conn,
            cursor=cursor,
            **kwargs,
        )

    def save_team(
        self,
        team_id: str,
        team_name: str,
        user_id: str = "",
        owner_name: str = "",
        current_points: int = 0,
        team_value: int = 0,
    ) -> None:
        return self.port.save_team(
            team_id,
            team_name,
            user_id=user_id,
            owner_name=owner_name,
            current_points=current_points,
            team_value=team_value,
        )

    def save_round_ranking(
        self, round_number: int, championship_id: str, teams: List[Dict]
    ) -> None:
        return self.port.save_round_ranking(round_number, championship_id, teams)

    def get_team_standings_history(
        self, championship_id: str, window: Optional[int] = None
    ) -> List[Dict]:
        return self.port.get_team_standings_history(championship_id, window=window)

    def get_latest_matchday(self, championship_id: str) -> Optional[int]:
        return self.port.get_latest_matchday(championship_id)

    def get_team_by_id(self, team_id: str) -> Optional[Dict]:
        return self.port.get_team_by_id(team_id)

    def get_player_streak_data(
        self, championship_id: str, min_matchday: Optional[int] = None
    ) -> List[Dict]:
        return self.port.get_player_streak_data(championship_id, min_matchday=min_matchday)
