"""Infrastructure adapter for ``news-articles`` — the only module with SQL (BR1.3).

Hosts the raw SQL formerly inline in ``DataManagerV2.save_matchday_article`` /
``get_matchday_article`` / ``save_pressroom_news`` /
``get_matchday_data_for_news``, moved **verbatim** including each
``if db_type in ["postgresql", "postgres"]: ... else: (SQLite)`` engine branch
(BR1.2/FR1.4). Reuses the facade's ``DBConnection`` (read live via the ``db``
property) and the shared ``ensure_championship_exists`` helper, so the
production result is byte-for-byte identical (BR3.1).
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.data_manager.news_articles.domain.ports import NewsArticlesDataPort

logger = logging.getLogger(__name__)


class NewsArticlesAdapter(NewsArticlesDataPort):
    """Adapt the news-articles SQL (verbatim) to :class:`NewsArticlesDataPort`."""

    def __init__(self, dm: Optional[Any] = None) -> None:
        if dm is None:
            from app.services.data_manager_v2 import DataManagerV2

            dm = DataManagerV2(skip_init=True)
        self.dm = dm

    @property
    def db(self):
        return self.dm.db

    def save_matchday_article(
        self,
        championship_id: str,
        matchday: int,
        article: str,
        summary: Optional[Dict] = None,
        generated_at: Optional[datetime] = None,
    ) -> None:
        """Persist generated matchday humor article and optional structured summary."""
        if not championship_id or matchday is None or article is None:
            raise ValueError("championship_id, matchday and article are required")

        summary_json = json.dumps(summary) if summary else None
        generated_at = generated_at or datetime.now()

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            # Ensure championship exists to satisfy FK constraint
            self.dm.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    INSERT INTO matchday_articles
                        (championship_id, matchday, article, summary_json, generated_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (championship_id, matchday) DO UPDATE SET
                        article = EXCLUDED.article,
                        summary_json = EXCLUDED.summary_json,
                        generated_at = EXCLUDED.generated_at,
                        updated_at = EXCLUDED.updated_at
                """
            else:
                sql = """
                    INSERT OR REPLACE INTO matchday_articles
                        (championship_id, matchday, article, summary_json, generated_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                sql = self.db.adapt_params(sql)

            cursor.execute(
                sql,
                (
                    championship_id,
                    matchday,
                    article,
                    summary_json,
                    generated_at,
                    datetime.now(),
                ),
            )

    def get_matchday_article(self, championship_id: str, matchday: int) -> Optional[Dict[str, Any]]:
        """Retrieve stored matchday article and metadata."""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            sql = """
                SELECT article, summary_json, generated_at, updated_at
                FROM matchday_articles
                WHERE championship_id = ? AND matchday = ?
            """
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (championship_id, matchday))
            row = cursor.fetchone()

            if not row:
                return None

            if isinstance(row, tuple):
                article, summary_json, generated_at, updated_at = row
            else:
                article = row.get("article")
                summary_json = row.get("summary_json")
                generated_at = row.get("generated_at")
                updated_at = row.get("updated_at")

            return {
                "championship_id": championship_id,
                "matchday": matchday,
                "article": article,
                "summary": json.loads(summary_json) if summary_json else None,
                "generated_at": generated_at,
                "updated_at": updated_at,
            }

    def save_pressroom_news(self, championship_id: str, news_items: List[Dict]) -> None:
        """Save pressroom news (kept for compatibility but not in optimized schema)"""
        # Pressroom news is not critical for historical analysis
        # Can be stored in separate table if needed
        logger.info(f"Skipping {len(news_items)} pressroom news items (not in optimized schema)")

    def get_matchday_data_for_news(self, championship_id: str, matchday: int) -> Dict:
        """Get comprehensive matchday data for generating press news"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            # Get current standings
            if self.db.db_type in ["postgresql", "postgres"]:
                current_sql = """
                    SELECT 
                        t.team_id,
                        t.team_name,
                        u.username,
                        ts.position,
                        ts.points,
                        ts.points_this_matchday
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    LEFT JOIN users u ON t.user_id = u.user_id
                    WHERE ts.championship_id = %s AND ts.matchday = %s
                    ORDER BY ts.position
                """
            else:
                current_sql = """
                    SELECT 
                        t.team_id,
                        t.team_name,
                        u.username,
                        ts.position,
                        ts.points,
                        ts.points_this_matchday
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    LEFT JOIN users u ON t.user_id = u.user_id
                    WHERE ts.championship_id = ? AND ts.matchday = ?
                    ORDER BY ts.position
                """
            cursor.execute(current_sql, (championship_id, matchday))
            current_standings = []
            for row in cursor.fetchall():
                current_standings.append(
                    {
                        "team_id": row[0],
                        "team_name": row[1],
                        "username": row[2],
                        "position": row[3],
                        "points": row[4],
                        "points_this_matchday": row[5],
                    }
                )

            # Get previous matchday standings (if exists)
            if self.db.db_type in ["postgresql", "postgres"]:
                previous_sql = """
                    SELECT 
                        t.team_id,
                        ts.position,
                        ts.points
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    WHERE ts.championship_id = %s AND ts.matchday = %s
                """
            else:
                previous_sql = """
                    SELECT 
                        t.team_id,
                        ts.position,
                        ts.points
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    WHERE ts.championship_id = ? AND ts.matchday = ?
                """
            previous_standings = {}
            if matchday > 1:
                cursor.execute(previous_sql, (championship_id, matchday - 1))
                for row in cursor.fetchall():
                    previous_standings[row[0]] = {"position": row[1], "points": row[2]}

            # Get best players per team this matchday
            if self.db.db_type in ["postgresql", "postgres"]:
                best_players_sql = """
                    SELECT 
                        pp.team_id,
                        pp.player_id,
                        p.name as player_name,
                        pp.points as player_points,
                        t.team_name
                    FROM player_performance pp
                    JOIN players p ON pp.player_id = p.player_id
                    JOIN teams t ON pp.team_id = t.team_id
                    WHERE pp.championship_id = %s AND pp.matchday = %s AND pp.was_best_player = true
                    ORDER BY pp.points DESC
                """
            else:
                best_players_sql = """
                    SELECT 
                        pp.team_id,
                        pp.player_id,
                        p.name as player_name,
                        pp.points as player_points,
                        t.team_name
                    FROM player_performance pp
                    JOIN players p ON pp.player_id = p.player_id
                    JOIN teams t ON pp.team_id = t.team_id
                    WHERE pp.championship_id = ? AND pp.matchday = ? AND pp.was_best_player = true
                    ORDER BY pp.points DESC
                """
            cursor.execute(best_players_sql, (championship_id, matchday))
            best_players = []
            for row in cursor.fetchall():
                best_players.append(
                    {
                        "team_id": row[0],
                        "player_id": row[1],
                        "player_name": row[2],
                        "player_points": row[3],
                        "team_name": row[4],
                    }
                )

            # Get top scoring players this matchday
            if self.db.db_type in ["postgresql", "postgres"]:
                top_players_sql = """
                    SELECT 
                        pp.player_id,
                        p.name as player_name,
                        pp.points,
                        t.team_name
                    FROM player_performance pp
                    JOIN players p ON pp.player_id = p.player_id
                    JOIN teams t ON pp.team_id = t.team_id
                    WHERE pp.championship_id = %s AND pp.matchday = %s
                    ORDER BY pp.points DESC
                    LIMIT 10
                """
            else:
                top_players_sql = """
                    SELECT 
                        pp.player_id,
                        p.name as player_name,
                        pp.points,
                        t.team_name
                    FROM player_performance pp
                    JOIN players p ON pp.player_id = p.player_id
                    JOIN teams t ON pp.team_id = t.team_id
                    WHERE pp.championship_id = ? AND pp.matchday = ?
                    ORDER BY pp.points DESC
                    LIMIT 10
                """
            cursor.execute(top_players_sql, (championship_id, matchday))
            top_players = []
            for row in cursor.fetchall():
                top_players.append(
                    {
                        "player_id": row[0],
                        "player_name": row[1],
                        "points": row[2],
                        "team_name": row[3],
                    }
                )

            return {
                "matchday": matchday,
                "current_standings": current_standings,
                "previous_standings": previous_standings,
                "best_players": best_players,
                "top_players": top_players,
            }
