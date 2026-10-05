"""Infrastructure adapter for ``performance`` — the only module with SQL (BR1.3).

Hosts the raw SQL formerly inline in ``DataManagerV2.save_player_performance`` /
``save_player_performance_batch`` / ``get_player_performance_history``, moved
**verbatim** including each ``if db_type in ["postgresql", "postgres"]: ...
else: (SQLite)`` engine branch and the ``psycopg2.extras.execute_values`` batch
path (BR1.2/FR1.4). Reuses the facade's ``DBConnection`` (``db`` property),
``ensure_championship_exists``, and ``get_latest_matchday`` so the production
result is byte-for-byte identical (BR3.1).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.data_manager.performance.domain.ports import PerformanceDataPort


class PerformanceAdapter(PerformanceDataPort):
    """Adapt the performance SQL (verbatim) to :class:`PerformanceDataPort`."""

    def __init__(self, dm: Optional[Any] = None) -> None:
        if dm is None:
            from app.services.data_manager_v2 import DataManagerV2

            dm = DataManagerV2(skip_init=True)
        self.dm = dm

    @property
    def db(self):
        return self.dm.db

    def save_player_performance(
        self,
        championship_id: str,
        player_id: str,
        team_id: str,
        matchday: int,
        points: int,
        value: int = None,
        was_best_player: bool = False,
        **kwargs,
    ) -> None:
        """Save player performance for a specific matchday (single record)"""
        self.save_player_performance_batch(
            championship_id,
            [
                {
                    "player_id": player_id,
                    "team_id": team_id,
                    "matchday": matchday,
                    "points": points,
                    "value": value,
                    "was_best_player": was_best_player,
                }
            ],
        )

    def save_player_performance_batch(self, championship_id: str, records: List[Dict]) -> int:
        """Save multiple player performance records in a single transaction (batch)."""
        if not records:
            return 0

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            self.dm.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)

            now = datetime.now()
            values = []
            for r in records:
                values.append(
                    (
                        championship_id,
                        r["player_id"],
                        r["team_id"],
                        r["matchday"],
                        r["points"],
                        r.get("value"),
                        bool(r.get("was_best_player", False)),
                        now,
                    )
                )

            if self.db.db_type in ["postgresql", "postgres"]:
                from psycopg2.extras import execute_values

                raw_cursor = cursor._cursor if hasattr(cursor, "_cursor") else cursor
                execute_values(
                    raw_cursor,
                    """
                    INSERT INTO player_performance 
                    (championship_id, player_id, team_id, matchday, points, value, was_best_player, recorded_at)
                    VALUES %s
                    ON CONFLICT (championship_id, player_id, team_id, matchday) DO UPDATE SET
                        points = EXCLUDED.points,
                        value = EXCLUDED.value,
                        was_best_player = EXCLUDED.was_best_player,
                        recorded_at = EXCLUDED.recorded_at
                """,
                    values,
                    page_size=200,
                )
            else:
                cursor.executemany(
                    """
                    INSERT OR REPLACE INTO player_performance 
                    (championship_id, player_id, team_id, matchday, points, value, was_best_player, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    values,
                )

            return len(values)

    def get_player_performance_history(
        self,
        championship_id: str,
        player_ids: Optional[List[str]] = None,
        window: Optional[int] = None,
    ) -> List[Dict]:
        """Return player performance records filtered by players and limited matchdays"""
        max_matchday = self.dm.get_latest_matchday(championship_id)
        params: List[Any] = [championship_id]
        filters = []

        if player_ids:
            placeholders = ",".join(["?"] * len(player_ids))
            filters.append(f"player_id IN ({placeholders})")
            params.extend(player_ids)

        if window and max_matchday:
            min_matchday = max_matchday - window + 1
            filters.append("matchday >= ?")
            params.append(min_matchday)

        filter_clause = " AND " + " AND ".join(filters) if filters else ""

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = f"""
                SELECT player_id, team_id, matchday, points, value, was_best_player
                FROM player_performance
                WHERE championship_id = ?{filter_clause}
                ORDER BY player_id, matchday
            """
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

        performances = []
        for row in rows:
            performances.append(
                {
                    "player_id": row[0],
                    "team_id": row[1],
                    "matchday": row[2],
                    "points": row[3],
                    "value": row[4],
                    "was_best_player": bool(row[5]) if row[5] is not None else False,
                }
            )
        return performances
