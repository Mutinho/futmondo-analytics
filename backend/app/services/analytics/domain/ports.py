"""Consumer-owned data port for the analytics context (BR2.1, BR2.3).

``AnalyticsDataPort`` is a structural :class:`typing.Protocol` describing ONLY
the data operations the analytics calculations consume. It is defined in the
domain layer and imports neither ``infrastructure/`` nor any framework, and it
contains no SQL (BR2.1, BR2.2). The application layer depends on this
abstraction, not on the concrete ``DataManagerV2`` (dependency inversion,
BR2.3); the concrete :class:`~app.services.analytics.infrastructure.data_manager_adapter.DataManagerAnalyticsAdapter`
implements it.

The first eleven methods delegate to the existing ``DataManagerV2`` surface
verbatim. The two ``fetch_*`` methods replace the two raw ``cursor.execute``
reads that previously lived inline in ``analytics_service.py`` — they are the
port's expression of "the teams lookup" and "batch player info", implemented
with raw SQL only inside the adapter (BR2.2, BR1.2).
"""

from typing import Dict, List, Optional, Protocol


class AnalyticsDataPort(Protocol):
    """Structural type of the data surface the analytics context consumes."""

    # --- Delegated DataManagerV2 reads ------------------------------------
    def get_team_standings_history(
        self, championship_id: str, window: Optional[int] = None
    ) -> List[Dict]: ...

    def get_latest_matchday(self, championship_id: str) -> Optional[int]: ...

    def get_team_by_id(self, team_id: str) -> Optional[Dict]: ...

    def get_player_by_id(self, player_id: str) -> Optional[Dict]: ...

    def get_all_users_with_points(self, championship_id: str) -> List[Dict]: ...

    def get_transactions_raw(
        self, championship_id: str, days: Optional[int] = None
    ) -> List[Dict]: ...

    def get_clausulable_player_stats(self, championship_id: str) -> List[Dict]: ...

    def get_clauses_raw(self, championship_id: str, days: Optional[int] = None) -> List[Dict]: ...

    def get_free_agent_candidates(self, championship_id: str) -> List[Dict]: ...

    def get_player_performance_history(
        self, championship_id: str, window: Optional[int] = None
    ) -> List[Dict]: ...

    def get_player_streak_data(
        self, championship_id: str, min_matchday: Optional[int] = None
    ) -> List[Dict]: ...

    def get_match_odds(
        self,
        championship_id: str,
        matchday: Optional[int] = None,
        upcoming_only: bool = False,
    ) -> List[Dict]: ...

    # --- Raw reads relocated behind the port (BR2.2, BR1.2) ---------------
    def fetch_all_teams(self) -> Dict[str, Dict]:
        """Return ``{team_id: {team_id, user_id, team_name}}`` for every team.

        Replaces the former inline ``SELECT team_id, user_id, team_name FROM
        teams`` of ``_safe_team_info``.
        """
        ...

    def fetch_players_by_ids(self, player_ids: List[str]) -> Dict[str, Dict]:
        """Return ``{player_id: {name, real_team_id, value}}`` for the given ids.

        Replaces the former inline ``SELECT player_id, name, real_team_id, value
        FROM players WHERE player_id IN (...)`` of ``get_market_watchlist``.
        Returns an empty mapping when ``player_ids`` is empty.
        """
        ...
