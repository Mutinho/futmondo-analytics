"""Infrastructure adapter for ``teams-standings`` — the only module with SQL (BR1.3).

Hosts the raw SQL formerly inline in the ``DataManagerV2`` standings methods,
moved **verbatim** including the engine branch (BR1.2/FR1.4), the
``get_connection().__enter__()`` same-transaction path, and the legacy bare
``except`` paths (BR3.2). Cross-responsibility helpers (``ensure_championship_exists``,
``_ensure_user``, ``save_team_standing``, ``get_latest_matchday``) are reached
live via ``self.dm`` so production behavior is byte-for-byte identical (BR3.1).
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.data_manager.teams_standings.domain.ports import TeamsStandingsDataPort

logger = logging.getLogger(__name__)


class TeamsStandingsAdapter(TeamsStandingsDataPort):
    """Adapt the teams/standings SQL (verbatim) to the port."""

    def __init__(self, dm: Optional[Any] = None) -> None:
        if dm is None:
            from app.services.data_manager_v2 import DataManagerV2

            dm = DataManagerV2(skip_init=True)
        self.dm = dm

    @property
    def db(self):
        return self.dm.db

    def save_team_standing(
        self,
        championship_id: str,
        team_id: str,
        matchday: int,
        position: int,
        points: int,
        points_this_matchday: int = 0,
        team_value: int = None,
        conn=None,
        cursor=None,
        **kwargs,
    ) -> None:
        """Save team standing for a specific matchday

        Args:
            conn: Optional existing database connection (for same transaction)
            cursor: Optional existing cursor (for same transaction)
        """
        use_existing = conn is not None and cursor is not None

        if not use_existing:
            conn = self.db.get_connection().__enter__()
            cursor = self.db.get_cursor(conn)
            should_close = True
        else:
            should_close = False

        try:
            # Ensure championship exists in the same transaction
            self.dm.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)

            # Extra safety: insert championship record directly (idempotent)
            if self.db.db_type in ["postgresql", "postgres"]:
                cursor.execute(
                    """
                    INSERT INTO championships (championship_id, name, created_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (championship_id) DO NOTHING
                    """,
                    (championship_id, championship_id, datetime.now()),
                )
            else:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO championships (championship_id, name, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (championship_id, championship_id, datetime.now()),
                )

            sql = """
                INSERT INTO team_standings 
                (championship_id, team_id, matchday, position, points, points_this_matchday, team_value, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            sql = self.db.adapt_params(sql)

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    INSERT INTO team_standings 
                    (championship_id, team_id, matchday, position, points, points_this_matchday, team_value, recorded_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (championship_id, team_id, matchday) DO UPDATE SET
                        position = EXCLUDED.position,
                        points = EXCLUDED.points,
                        points_this_matchday = EXCLUDED.points_this_matchday,
                        team_value = EXCLUDED.team_value,
                        recorded_at = EXCLUDED.recorded_at
                """
            else:
                sql = """
                    INSERT OR REPLACE INTO team_standings 
                    (championship_id, team_id, matchday, position, points, points_this_matchday, team_value, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                sql = self.db.adapt_params(sql)

            now = datetime.now()
            cursor.execute(
                sql,
                (
                    championship_id,
                    team_id,
                    matchday,
                    position,
                    points,
                    points_this_matchday,
                    team_value,
                    now,
                ),
            )

            if not use_existing:
                conn.commit()
        finally:
            if should_close:
                try:
                    conn.close()
                except:
                    pass

    def save_team(
        self,
        team_id: str,
        team_name: str,
        user_id: str = "",
        owner_name: str = "",
        current_points: int = 0,
        team_value: int = 0,
    ):
        """Save team information"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            # First ensure user exists
            if user_id:
                self.dm._ensure_user(user_id, owner_name or team_name)

            sql = """
                INSERT INTO teams (team_id, user_id, team_name, initial_budget, last_updated)
                VALUES (?, ?, ?, ?, ?)
            """
            sql = self.db.adapt_params(sql)

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    INSERT INTO teams (team_id, user_id, team_name, initial_budget, last_updated)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (team_id) DO UPDATE SET
                        user_id = EXCLUDED.user_id,
                        team_name = EXCLUDED.team_name,
                        initial_budget = EXCLUDED.initial_budget,
                        last_updated = EXCLUDED.last_updated
                """
            else:
                sql = """
                    INSERT OR REPLACE INTO teams (team_id, user_id, team_name, initial_budget, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                """
                sql = self.db.adapt_params(sql)

            now = datetime.now()
            cursor.execute(sql, (team_id, user_id or None, team_name, 270000000, now))

    def save_round_ranking(self, round_number: int, championship_id: str, teams: List[Dict]):
        """Save round ranking data for historical analysis"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            # Ensure championship exists in the same transaction (MUST be first)
            self.dm.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)

            # Commit championship creation if it was just created (to ensure it's visible)
            conn.commit()

            now = datetime.now()

            def _safe_int(value):
                try:
                    return int(value)
                except (TypeError, ValueError):
                    return 0

            for team in teams:
                team_id = team.get("id") or team.get("teamid") or (team.get("team") or {}).get("id")
                position = team.get("position", 0)
                raw_total_points = team.get("points")
                round_points_only = team.get("roundPoints")

                if not team_id:
                    continue

                prev_points_total = 0
                if round_number > 1:
                    sql_prev = """
                        SELECT points FROM team_standings 
                        WHERE championship_id = ? AND team_id = ? AND matchday = ?
                    """
                    sql_prev = self.db.adapt_params(sql_prev)
                    cursor.execute(sql_prev, (championship_id, team_id, round_number - 1))
                    prev_row = cursor.fetchone()
                    if prev_row:
                        prev_points_total = (
                            prev_row[0]
                            if isinstance(prev_row, tuple)
                            else prev_row.get("points", 0)
                        )

                if round_points_only is not None:
                    points_this_matchday = _safe_int(round_points_only)
                    points = prev_points_total + points_this_matchday
                elif raw_total_points is not None:
                    # Ranking API returns points for THIS round only (not accumulated)
                    points_this_matchday = _safe_int(raw_total_points)
                    points = prev_points_total + points_this_matchday
                else:
                    points_this_matchday = 0
                    points = prev_points_total

                self.dm.save_team_standing(
                    championship_id=championship_id,
                    team_id=team_id,
                    matchday=round_number,
                    position=position,
                    points=points,
                    points_this_matchday=points_this_matchday,
                    team_value=team.get("value", 0),
                    conn=conn,
                    cursor=cursor,
                )

            # Commit all team standings
            conn.commit()

        logger.info(f"Saved round {round_number} ranking for {len(teams)} teams")

    def get_latest_matchday(self, championship_id: str) -> Optional[int]:
        """Return the latest matchday available in team_standings"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = "SELECT MAX(matchday) FROM team_standings WHERE championship_id = ?"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (championship_id,))
            row = cursor.fetchone()
            if row and row[0] is not None:
                return int(row[0])
        return None

    def get_team_standings_history(
        self, championship_id: str, window: Optional[int] = None
    ) -> List[Dict]:
        """Return standings history for each team, optionally limited to last `window` matchdays"""
        max_matchday = self.dm.get_latest_matchday(championship_id)
        params: List[Any] = [championship_id]
        condition = ""
        if window and max_matchday:
            min_matchday = max_matchday - window + 1
            condition = " AND matchday >= ?"
            params.append(min_matchday)

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = f"""
                SELECT team_id, matchday, position, points, points_this_matchday, team_value
                FROM team_standings
                WHERE championship_id = ?{condition}
                ORDER BY team_id, matchday
            """
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

        history = []
        for row in rows:
            history.append(
                {
                    "team_id": row[0],
                    "matchday": row[1],
                    "position": row[2],
                    "points": row[3],
                    "points_this_matchday": row[4],
                    "team_value": row[5],
                }
            )
        return history

    def get_team_by_id(self, team_id: str) -> Optional[Dict]:
        if not team_id:
            return None

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = "SELECT team_id, user_id, team_name FROM teams WHERE team_id = ?"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (team_id,))
            row = cursor.fetchone()

        if not row:
            return None

        return {"team_id": row[0], "user_id": row[1], "team_name": row[2]}

    def get_player_streak_data(
        self, championship_id: str, min_matchday: Optional[int] = None
    ) -> List[Dict]:
        """Return player performance ordered by matchday for streak calculations"""
        params: List[Any] = [championship_id]
        condition = ""
        if min_matchday:
            condition = " AND matchday >= ?"
            params.append(min_matchday)

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = f"""
                SELECT player_id, matchday, points
                FROM player_performance
                WHERE championship_id = ?{condition}
                ORDER BY player_id, matchday
            """
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

        data = []
        for row in rows:
            data.append({"player_id": row[0], "matchday": row[1], "points": row[2]})
        return data
