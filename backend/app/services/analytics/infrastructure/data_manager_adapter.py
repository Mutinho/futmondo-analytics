"""Infrastructure adapter implementing :class:`AnalyticsDataPort` (BR2.2).

This is the ONLY module in the analytics context that touches raw SQL. It wraps
the current ``DataManagerV2`` facade (Wave 1 does not yet decompose
``data_manager`` — that is Wave 4), delegating the eleven data reads verbatim,
and hosts the two raw ``SELECT`` statements that previously lived inline in
``analytics_service.py`` (``_safe_team_info`` and ``get_market_watchlist``),
moved unchanged so they return the exact same rows (BR1.2).

The two raw reads go through ``db.adapt_params`` exactly like
``prizes/team_prizes_writer.py``: the SQL is written with ``?`` placeholders and
adapted to ``%s`` for PostgreSQL by ``adapt_params`` (a no-op for the parameter
count of the teams query, and the same ``?`` -> ``%s`` transform for the players
query). This keeps the production result identical to the former inline
``%s``-based query while remaining testable against the in-memory SQLite fake.
"""

from typing import Dict, List, Optional

from app.services.analytics.domain.ports import AnalyticsDataPort
from app.services.data_manager_v2 import DataManagerV2


class DataManagerAnalyticsAdapter(AnalyticsDataPort):
    """Adapt ``DataManagerV2`` (+ two raw reads) to ``AnalyticsDataPort``."""

    def __init__(self, dm: Optional[DataManagerV2] = None, db_factory=None) -> None:
        """Create the adapter.

        Args:
            dm: The data manager to delegate reads to. Defaults to a fresh
                ``DataManagerV2()`` to preserve the historical no-arg behavior.
            db_factory: A zero-arg callable returning a ``DBConnection``-like
                object (``get_connection``/``get_cursor``/``adapt_params``).
                Defaults to the global ``db_connection.get_db`` singleton, so
                production behavior is unchanged. Injectable for testing.
        """
        self.dm = dm if dm is not None else DataManagerV2()
        self._db_factory = db_factory

    def _get_db(self):
        if self._db_factory is not None:
            return self._db_factory()
        from app.services.db_connection import get_db

        return get_db()

    # --- Delegated DataManagerV2 reads ------------------------------------
    def get_team_standings_history(
        self, championship_id: str, window: Optional[int] = None
    ) -> List[Dict]:
        return self.dm.get_team_standings_history(championship_id, window=window)

    def get_latest_matchday(self, championship_id: str) -> Optional[int]:
        return self.dm.get_latest_matchday(championship_id)

    def get_team_by_id(self, team_id: str) -> Optional[Dict]:
        return self.dm.get_team_by_id(team_id)

    def get_player_by_id(self, player_id: str) -> Optional[Dict]:
        return self.dm.get_player_by_id(player_id)

    def get_all_users_with_points(self, championship_id: str) -> List[Dict]:
        return self.dm.get_all_users_with_points(championship_id)

    def get_transactions_raw(self, championship_id: str, days: Optional[int] = None) -> List[Dict]:
        return self.dm.get_transactions_raw(championship_id, days=days)

    def get_clausulable_player_stats(self, championship_id: str) -> List[Dict]:
        return self.dm.get_clausulable_player_stats(championship_id)

    def get_clauses_raw(self, championship_id: str, days: Optional[int] = None) -> List[Dict]:
        return self.dm.get_clauses_raw(championship_id, days=days)

    def get_free_agent_candidates(self, championship_id: str) -> List[Dict]:
        return self.dm.get_free_agent_candidates(championship_id)

    def get_player_performance_history(
        self, championship_id: str, window: Optional[int] = None
    ) -> List[Dict]:
        return self.dm.get_player_performance_history(championship_id, window=window)

    def get_player_streak_data(
        self, championship_id: str, min_matchday: Optional[int] = None
    ) -> List[Dict]:
        return self.dm.get_player_streak_data(championship_id, min_matchday=min_matchday)

    def get_match_odds(
        self,
        championship_id: str,
        matchday: Optional[int] = None,
        upcoming_only: bool = False,
    ) -> List[Dict]:
        return self.dm.get_match_odds(
            championship_id, matchday=matchday, upcoming_only=upcoming_only
        )

    # --- Raw reads relocated here verbatim (BR2.2, BR1.2) -----------------
    def fetch_all_teams(self) -> Dict[str, Dict]:
        """Load every team as ``{team_id: {team_id, user_id, team_name}}``.

        Hosts the former inline ``SELECT team_id, user_id, team_name FROM teams``
        of ``_safe_team_info``, unchanged. On any error it returns an empty
        mapping, preserving the former defensive ``except Exception: pass`` that
        left the cache empty (registered debt, unchanged in this wave).
        """
        teams: Dict[str, Dict] = {}
        try:
            db = self._get_db()
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                cursor.execute(db.adapt_params("SELECT team_id, user_id, team_name FROM teams"))
                for row in cursor.fetchall():
                    teams[row[0]] = {
                        "team_id": row[0],
                        "user_id": row[1],
                        "team_name": row[2],
                    }
        except Exception:
            pass
        return teams

    def fetch_players_by_ids(self, player_ids: List[str]) -> Dict[str, Dict]:
        """Batch-load players as ``{player_id: {name, real_team_id, value}}``.

        Hosts the former inline ``SELECT player_id, name, real_team_id, value
        FROM players WHERE player_id IN (...)`` of ``get_market_watchlist``,
        unchanged. Returns an empty mapping for an empty id list, and on any
        error, preserving the former defensive ``except Exception: pass``.
        """
        player_info_map: Dict[str, Dict] = {}
        if not player_ids:
            return player_info_map
        try:
            db = self._get_db()
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                placeholders = ",".join(["?"] * len(player_ids))
                cursor.execute(
                    db.adapt_params(
                        "SELECT player_id, name, real_team_id, value FROM players "
                        f"WHERE player_id IN ({placeholders})"
                    ),
                    tuple(player_ids),
                )
                for row in cursor.fetchall():
                    player_info_map[row[0]] = {
                        "name": row[1],
                        "real_team_id": row[2],
                        "value": row[3] or 0,
                    }
        except Exception:
            pass
        return player_info_map
