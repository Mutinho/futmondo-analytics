"""Infrastructure adapter for ``players`` — the only module with SQL (BR1.3).

Hosts the raw SQL formerly inline in the ``DataManagerV2`` player methods, moved
**verbatim** including the engine branch (BR1.2/FR1.4), the PostgreSQL
``execute_values`` / SQLite ``executemany`` batch paths, and the legacy
``return None`` edges (BR3.2). The ``delete_orphan_players`` ``DELETE ... NOT IN``
set-replacement corruption point (BR3.3, OQ2 deferred) is moved **verbatim** and
is NOT elevated to the atomic reference pattern. ``ensure_championship_exists`` is
reached live via ``self.dm`` so production behavior is byte-for-byte identical
(BR3.1).
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.data_manager.players.domain.ports import PlayersDataPort

logger = logging.getLogger(__name__)


class PlayersAdapter(PlayersDataPort):
    """Adapt the players SQL (verbatim) to the port."""

    def __init__(self, dm: Optional[Any] = None) -> None:
        if dm is None:
            from app.services.data_manager_v2 import DataManagerV2

            dm = DataManagerV2(skip_init=True)
        self.dm = dm

    @property
    def db(self):
        return self.dm.db

    def save_player(self, player_data: Dict) -> str:
        """Save or update player information"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            player_id = player_data.get("id", "")
            if not player_id:
                return None

            sql = """
                INSERT INTO players (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            sql = self.db.adapt_params(sql)

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    INSERT INTO players (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (player_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        role = EXCLUDED.role,
                        real_team_id = EXCLUDED.real_team_id,
                        real_team_name = EXCLUDED.real_team_name,
                        slug = EXCLUDED.slug,
                        photo_url = EXCLUDED.photo_url,
                        last_updated = EXCLUDED.last_updated
                """
            else:
                sql = """
                    INSERT OR REPLACE INTO players (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                sql = self.db.adapt_params(sql)

            now = datetime.now()
            cursor.execute(
                sql,
                (
                    player_id,
                    player_data.get("name", ""),
                    player_data.get("role", ""),
                    player_data.get("teamId", ""),
                    player_data.get("team", ""),
                    player_data.get("slug", ""),
                    player_data.get("photo_url", ""),
                    now,
                ),
            )

            return player_id

    def save_players_batch(self, players: List[Dict]) -> int:
        """Save or update multiple players in a single transaction (batch upsert).

        Args:
            players: List of dicts with keys: id, name, role, real_team_id/teamId,
                     real_team_name/team, slug, photo_url/photo

        Returns:
            Number of players processed
        """
        if not players:
            return 0

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            now = datetime.now()

            if self.db.db_type in ["postgresql", "postgres"]:
                from psycopg2.extras import execute_values

                sql = """
                    INSERT INTO players (player_id, name, role, role2, real_team_id, real_team_name, slug, photo_url, value, last_updated)
                    VALUES %s
                    ON CONFLICT (player_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        role = EXCLUDED.role,
                        role2 = EXCLUDED.role2,
                        real_team_id = EXCLUDED.real_team_id,
                        real_team_name = EXCLUDED.real_team_name,
                        slug = EXCLUDED.slug,
                        photo_url = EXCLUDED.photo_url,
                        value = EXCLUDED.value,
                        last_updated = EXCLUDED.last_updated
                """
                values = []
                for p in players:
                    player_id = p.get("id", "")
                    if not player_id:
                        continue
                    values.append(
                        (
                            player_id,
                            p.get("name", ""),
                            p.get("role", ""),
                            p.get("role2", ""),
                            p.get("teamId", p.get("real_team_id", "")),
                            p.get("team", p.get("real_team_name", "")),
                            p.get("slug", ""),
                            p.get("photo", p.get("photo_url", "")),
                            p.get("value", 0) or 0,
                            now,
                        )
                    )

                # Use execute_values for efficient batch insert
                # Unwrap the _TursoCursorWrapper if present
                raw_cursor = cursor._cursor if hasattr(cursor, "_cursor") else cursor
                execute_values(raw_cursor, sql, values, page_size=100)
            else:
                # SQLite/Turso: use executemany
                sql = """
                    INSERT OR REPLACE INTO players 
                    (player_id, name, role, role2, real_team_id, real_team_name, slug, photo_url, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                values = []
                for p in players:
                    player_id = p.get("id", "")
                    if not player_id:
                        continue
                    values.append(
                        (
                            player_id,
                            p.get("name", ""),
                            p.get("role", ""),
                            p.get("role2", ""),
                            p.get("teamId", p.get("real_team_id", "")),
                            p.get("team", p.get("real_team_name", "")),
                            p.get("slug", ""),
                            p.get("photo", p.get("photo_url", "")),
                            now,
                        )
                    )
                cursor.executemany(sql, values)

            return len(values)

    def delete_orphan_players(self, live_player_ids: List[str]) -> int:
        """Delete players that are neither in the current API list nor referenced
        by any historical table.

        Players not returned by the API are only removed if they have NO rows in
        transactions / player_performance / team_rosters / dream_teams_mvps /
        player_championship_stats. Players with history are always kept.

        Args:
            live_player_ids: player_ids returned by the current API sync.

        Returns:
            Number of orphan players deleted.
        """
        if not live_player_ids:
            # Safety: never wipe the table if the API returned nothing.
            return 0

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    DELETE FROM players p
                    WHERE p.player_id <> ALL(%s)
                      AND NOT EXISTS (SELECT 1 FROM transactions t WHERE t.player_id = p.player_id)
                      AND NOT EXISTS (SELECT 1 FROM player_performance pp WHERE pp.player_id = p.player_id)
                      AND NOT EXISTS (SELECT 1 FROM team_rosters tr WHERE tr.player_id = p.player_id)
                      AND NOT EXISTS (SELECT 1 FROM dream_teams_mvps dm WHERE dm.player_id = p.player_id)
                      AND NOT EXISTS (SELECT 1 FROM player_championship_stats pc WHERE pc.player_id = p.player_id)
                """
                cursor.execute(sql, (list(live_player_ids),))
            else:
                placeholders = ",".join("?" for _ in live_player_ids)
                sql = f"""
                    DELETE FROM players
                    WHERE player_id NOT IN ({placeholders})
                      AND player_id NOT IN (SELECT player_id FROM transactions)
                      AND player_id NOT IN (SELECT player_id FROM player_performance)
                      AND player_id NOT IN (SELECT player_id FROM team_rosters)
                      AND player_id NOT IN (SELECT player_id FROM dream_teams_mvps)
                      AND player_id NOT IN (SELECT player_id FROM player_championship_stats)
                """
                cursor.execute(sql, tuple(live_player_ids))
            deleted = cursor.rowcount if cursor.rowcount is not None else 0
            return deleted

    def save_players(self, players: List[Dict]):
        """Save players data to database (optimized for historical analysis)"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            now = datetime.now()

            for player in players:
                player_id = player.get("id", "")
                if not player_id:
                    continue

                # Extract photo URL
                photo_filename = player.get("photo", "")
                photo_url = None
                if photo_filename:
                    PHOTO_BASE_URL = "https://static01.mondocore.com/futmondo/img/faces/64"
                    if photo_filename.startswith("http"):
                        photo_url = photo_filename
                    elif photo_filename.startswith("/"):
                        photo_url = f"https://static01.mondocore.com{photo_filename}"
                    elif "." in photo_filename:
                        photo_url = f"{PHOTO_BASE_URL}/{photo_filename}"

                sql = """
                    INSERT INTO players 
                    (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                sql = self.db.adapt_params(sql)

                if self.db.db_type in ["postgresql", "postgres"]:
                    sql = """
                        INSERT INTO players 
                        (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (player_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            role = EXCLUDED.role,
                            real_team_id = EXCLUDED.real_team_id,
                            real_team_name = EXCLUDED.real_team_name,
                            slug = EXCLUDED.slug,
                            photo_url = EXCLUDED.photo_url,
                            last_updated = EXCLUDED.last_updated
                    """
                else:
                    sql = """
                        INSERT OR REPLACE INTO players 
                        (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    sql = self.db.adapt_params(sql)

                cursor.execute(
                    sql,
                    (
                        player_id,
                        player.get("name", ""),
                        player.get("role", ""),
                        player.get("teamId", ""),
                        player.get("team", ""),
                        player.get("slug", ""),
                        photo_url,
                        now,
                    ),
                )

        logger.info(f"Saved {len(players)} players to database")

    def get_all_players_with_points(self, championship_id: str) -> List[Dict]:
        """Get all players with their total points"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    SELECT 
                        p.id as player_id,
                        p.name as player_name,
                        p.role,
                        p.team,
                        COALESCE(SUM(pp.points), 0) as total_points
                    FROM players p
                    LEFT JOIN player_performance pp ON p.id = pp.player_id AND (pp.championship_id = %s OR pp.championship_id IS NULL)
                    GROUP BY p.id, p.name, p.role, p.team
                    ORDER BY total_points DESC
                """
            else:
                sql = """
                    SELECT 
                        p.id as player_id,
                        p.name as player_name,
                        p.role,
                        p.team,
                        COALESCE(SUM(pp.points), 0) as total_points
                    FROM players p
                    LEFT JOIN player_performance pp ON p.id = pp.player_id AND (pp.championship_id = ? OR pp.championship_id IS NULL)
                    GROUP BY p.id, p.name, p.role, p.team
                    ORDER BY total_points DESC
                """

            cursor.execute(sql, (championship_id,))
            results = cursor.fetchall()

            players = []
            for row in results:
                players.append(
                    {
                        "player_id": row[0],
                        "player_name": row[1],
                        "role": row[2],
                        "team": row[3],
                        "total_points": row[4] if row[4] else 0,
                    }
                )

            return players

    def get_player_by_id(self, player_id: str) -> Optional[Dict]:
        if not player_id:
            return None

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = """
                SELECT player_id, name, role, real_team_name, real_team_id, photo_url
                FROM players
                WHERE player_id = ?
            """
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (player_id,))
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "player_id": row[0],
            "name": row[1],
            "role": row[2],
            "team": row[3],
            "team_id": row[4],
            "photo_url": row[5],
        }

    def save_player_championship_stats(self, championship_id: str, player_stats: List[Dict]):
        """Persist clause and average metrics for players in a championship (batch)."""
        if not player_stats:
            return

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            # Ensure championship exists so FK constraints succeed
            self.dm.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)

            now = datetime.now()
            values = []

            for data in player_stats:
                player_id = data.get("player_id")
                if not player_id:
                    continue

                owner_team_id = data.get("owner_team_id") or None
                owner_team_name = data.get("owner_team_name") or (
                    owner_team_id if owner_team_id else "Free Agent"
                )
                owner_user_id = data.get("owner_user_id") or owner_team_id

                clause_price = data.get("clause_price")
                suggested_clause = data.get("suggested_clause")
                average_last_five = data.get("average_last_five")
                average_overall = data.get("average_overall")
                clause_date = data.get("clause_date")

                try:
                    clause_price = int(clause_price) if clause_price is not None else None
                except (TypeError, ValueError):
                    clause_price = None
                try:
                    suggested_clause = (
                        int(suggested_clause) if suggested_clause is not None else None
                    )
                except (TypeError, ValueError):
                    suggested_clause = None
                try:
                    average_last_five = (
                        float(average_last_five) if average_last_five is not None else None
                    )
                except (TypeError, ValueError):
                    average_last_five = None
                try:
                    average_overall = (
                        float(average_overall) if average_overall is not None else None
                    )
                except (TypeError, ValueError):
                    average_overall = None

                values.append(
                    (
                        championship_id,
                        player_id,
                        owner_team_id,
                        owner_team_name,
                        owner_user_id,
                        clause_price,
                        suggested_clause,
                        average_last_five,
                        average_overall,
                        clause_date,
                        now,
                    )
                )

            if not values:
                return

            if self.db.db_type in ["postgresql", "postgres"]:
                from psycopg2.extras import execute_values

                raw_cursor = cursor._cursor if hasattr(cursor, "_cursor") else cursor
                execute_values(
                    raw_cursor,
                    """
                    INSERT INTO player_championship_stats
                    (championship_id, player_id, owner_team_id, owner_team_name, owner_user_id,
                     clause_price, suggested_clause, average_last_five, average_overall, clause_date, updated_at)
                    VALUES %s
                    ON CONFLICT (championship_id, player_id) DO UPDATE SET
                        owner_team_id = EXCLUDED.owner_team_id,
                        owner_team_name = EXCLUDED.owner_team_name,
                        owner_user_id = EXCLUDED.owner_user_id,
                        clause_price = EXCLUDED.clause_price,
                        suggested_clause = EXCLUDED.suggested_clause,
                        average_last_five = EXCLUDED.average_last_five,
                        average_overall = EXCLUDED.average_overall,
                        clause_date = EXCLUDED.clause_date,
                        updated_at = EXCLUDED.updated_at
                """,
                    values,
                    page_size=100,
                )
            else:
                sql = """
                    INSERT OR REPLACE INTO player_championship_stats
                    (championship_id, player_id, owner_team_id, owner_team_name, owner_user_id,
                     clause_price, suggested_clause, average_last_five, average_overall, clause_date, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.executemany(sql, values)

            logger.info(f"Saved {len(values)} player championship stats for {championship_id}")
