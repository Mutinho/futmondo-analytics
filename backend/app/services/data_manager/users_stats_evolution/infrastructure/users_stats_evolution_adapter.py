"""Infrastructure adapter for ``users-stats-evolution`` — the only module with SQL (BR1.3).

Hosts the raw SQL formerly inline in the ``DataManagerV2`` user/stats/evolution
methods, moved **verbatim** including the engine branch (BR1.2/FR1.4) and the
legacy broad ``except`` paths (BR3.2). This module also OWNS the shared user
helpers ``_ensure_user`` / ``_get_or_create_user_id`` (exposed here as
``ensure_user`` / ``get_or_create_user_id``); the facade keeps thin private
delegators so earlier-extracted adapters that call ``self.dm._ensure_user`` keep
working unchanged (BR3.1). Cross-responsibility ``get_team_by_id`` is reached
live via ``self.dm``; ``get_user_by_id`` is local to this module.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional

from app.services.data_manager.users_stats_evolution.domain.ports import (
    UsersStatsEvolutionDataPort,
)

logger = logging.getLogger(__name__)


class UsersStatsEvolutionAdapter(UsersStatsEvolutionDataPort):
    """Adapt the user/stats/evolution SQL (verbatim) to the port."""

    def __init__(self, dm: Optional[Any] = None) -> None:
        if dm is None:
            from app.services.data_manager_v2 import DataManagerV2

            dm = DataManagerV2(skip_init=True)
        self.dm = dm

    @property
    def db(self):
        return self.dm.db

    def ensure_user(self, user_id: str, username: str) -> None:
        """Ensure user exists in database (former ``_ensure_user``)."""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            sql = """
                INSERT INTO users (user_id, username, last_updated)
                VALUES (?, ?, ?)
            """
            sql = self.db.adapt_params(sql)

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    INSERT INTO users (user_id, username, last_updated)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = EXCLUDED.username,
                        last_updated = EXCLUDED.last_updated
                """
            else:
                sql = """
                    INSERT OR REPLACE INTO users (user_id, username, last_updated)
                    VALUES (?, ?, ?)
                """
                sql = self.db.adapt_params(sql)

            from datetime import datetime

            now = datetime.now()
            cursor.execute(sql, (user_id, username, now))

    def get_or_create_user_id(self, user_id_or_username: str, username: str) -> str:
        """Get or create user ID from username or ID (former ``_get_or_create_user_id``)."""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            # Check if user_id_or_username is already a user_id (UUID format)
            if len(user_id_or_username) == 36 and user_id_or_username.count("-") == 4:
                # Already a UUID
                sql = "SELECT user_id FROM users WHERE user_id = ?"
                sql = self.db.adapt_params(sql)
                cursor.execute(sql, (user_id_or_username,))
                row = cursor.fetchone()
                if row:
                    return user_id_or_username

            # Check by username
            sql = "SELECT user_id FROM users WHERE username = ?"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (username,))
            row = cursor.fetchone()
            if row:
                return row[0] if isinstance(row, tuple) else row.get("user_id")

            # Create new user
            user_id = str(uuid.uuid4())
            self.ensure_user(user_id, username)
            return user_id

    def get_user_id_by_name(self, user_name: str) -> Optional[Dict[str, str]]:
        """Get user_id and team_id by user name (username or team_name)

        Uses case-insensitive matching and creates user if not found.

        Returns:
            Dict with 'user_id' and 'team_id', or None if not found and couldn't create
        """
        if not user_name:
            return None

        # Normalize name (trim, lowercase for comparison)
        normalized_name = user_name.strip()

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            # Try exact match first (case-insensitive)
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = "SELECT user_id FROM users WHERE LOWER(username) = LOWER(?)"
            else:
                sql = "SELECT user_id FROM users WHERE LOWER(username) = LOWER(?)"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (normalized_name,))
            row = cursor.fetchone()

            if row:
                user_id = row[0] if isinstance(row, tuple) else row.get("user_id")

                # Try to find team_id for this user
                sql = "SELECT team_id FROM teams WHERE user_id = ?"
                sql = self.db.adapt_params(sql)
                cursor.execute(sql, (user_id,))
                team_row = cursor.fetchone()
                team_id = (
                    team_row[0]
                    if team_row and isinstance(team_row, tuple)
                    else (team_row.get("team_id") if team_row else None)
                )

                return {"user_id": user_id, "team_id": team_id}

            # Try to find by team_name (case-insensitive)
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = "SELECT team_id, user_id FROM teams WHERE LOWER(team_name) = LOWER(?)"
            else:
                sql = "SELECT team_id, user_id FROM teams WHERE LOWER(team_name) = LOWER(?)"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (normalized_name,))
            row = cursor.fetchone()

            if row:
                team_id = row[0] if isinstance(row, tuple) else row.get("team_id")
                user_id = row[1] if isinstance(row, tuple) else row.get("user_id")
                return {"user_id": user_id or team_id, "team_id": team_id}

            # Try partial match (contains)
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = "SELECT user_id FROM users WHERE LOWER(username) LIKE LOWER(?)"
            else:
                sql = "SELECT user_id FROM users WHERE LOWER(username) LIKE LOWER(?)"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (f"%{normalized_name}%",))
            row = cursor.fetchone()

            if row:
                user_id = row[0] if isinstance(row, tuple) else row.get("user_id")
                sql = "SELECT team_id FROM teams WHERE user_id = ?"
                sql = self.db.adapt_params(sql)
                cursor.execute(sql, (user_id,))
                team_row = cursor.fetchone()
                team_id = (
                    team_row[0]
                    if team_row and isinstance(team_row, tuple)
                    else (team_row.get("team_id") if team_row else None)
                )
                return {"user_id": user_id, "team_id": team_id}

            # Try partial match on team_name
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = "SELECT team_id, user_id FROM teams WHERE LOWER(team_name) LIKE LOWER(?)"
            else:
                sql = "SELECT team_id, user_id FROM teams WHERE LOWER(team_name) LIKE LOWER(?)"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (f"%{normalized_name}%",))
            row = cursor.fetchone()

            if row:
                team_id = row[0] if isinstance(row, tuple) else row.get("team_id")
                user_id = row[1] if isinstance(row, tuple) else row.get("user_id")
                return {"user_id": user_id or team_id, "team_id": team_id}

            # If not found, create user and team
            logger.info(f"Creating new user/team for name: {normalized_name}")
            user_id = str(uuid.uuid4())
            team_id = str(uuid.uuid4())

            # Create user
            sql = "INSERT INTO users (user_id, username) VALUES (?, ?)"
            sql = self.db.adapt_params(sql)
            try:
                cursor.execute(sql, (user_id, normalized_name))
            except Exception as e:
                # User might already exist, try to get it
                logger.warning(f"Could not create user {normalized_name}: {e}")
                sql = "SELECT user_id FROM users WHERE username = ?"
                sql = self.db.adapt_params(sql)
                cursor.execute(sql, (normalized_name,))
                row = cursor.fetchone()
                if row:
                    user_id = row[0] if isinstance(row, tuple) else row.get("user_id")
                else:
                    return None

            # Create team
            sql = "INSERT INTO teams (team_id, team_name, user_id) VALUES (?, ?, ?)"
            sql = self.db.adapt_params(sql)
            try:
                cursor.execute(sql, (team_id, normalized_name, user_id))
            except Exception as e:
                # Team might already exist
                logger.warning(f"Could not create team {normalized_name}: {e}")
                sql = "SELECT team_id FROM teams WHERE team_name = ? OR user_id = ?"
                sql = self.db.adapt_params(sql)
                cursor.execute(sql, (normalized_name, user_id))
                row = cursor.fetchone()
                if row:
                    team_id = row[0] if isinstance(row, tuple) else row.get("team_id")
                else:
                    team_id = user_id  # Use user_id as fallback

            conn.commit()
            return {"user_id": user_id, "team_id": team_id}

    def get_users_unique_players_stats(self, championship_id: str) -> List[Dict]:
        """Get statistics of unique players aligned by each user/team"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            unique_players_sql = """
                SELECT 
                    COALESCE(t.team_id, tr.team_id) as team_id,
                    COALESCE(t.team_name, tr.team_id) as team_name,
                    COALESCE(t.user_id, tr.team_id) as user_id,
                    u.username,
                    COUNT(DISTINCT tr.player_id) as unique_players_count
                FROM team_rosters tr
                LEFT JOIN teams t ON tr.team_id = t.team_id
                LEFT JOIN users u ON COALESCE(t.user_id, tr.team_id) = u.user_id
                WHERE tr.championship_id = ?
                GROUP BY COALESCE(t.team_id, tr.team_id), COALESCE(t.team_name, tr.team_id), COALESCE(t.user_id, tr.team_id), u.username
            """
            unique_players_sql = self.db.adapt_sql(unique_players_sql)
            unique_players_sql = self.db.adapt_params(unique_players_sql)
            cursor.execute(unique_players_sql, (championship_id,))
            results = cursor.fetchall()

            stats = {}
            for row in results:
                team_id = row[0]
                stats[team_id] = {
                    "team_id": team_id,
                    "team_name": row[1] if row[1] and row[1] != team_id else None,
                    "user_id": row[2],
                    "username": row[3],
                    "unique_players_count": row[4],
                    "clauses_paid": 0,
                    "clauses_received": 0,
                    "total_clauses_paid": 0,
                    "total_clauses_received": 0,
                    "transaction_count": 0,
                    "total_spent": 0,
                    "total_received": 0,
                    "transaction_profit": 0,
                }

            clauses_sql = """
                SELECT 
                    COALESCE(payer_team_id, payer_user_id) as payer_id,
                    COALESCE(receiver_team_id, receiver_user_id) as receiver_id,
                    COUNT(*) as clause_count,
                    SUM(amount) as total_amount
                FROM clauses
                WHERE championship_id = ?
                GROUP BY COALESCE(payer_team_id, payer_user_id), COALESCE(receiver_team_id, receiver_user_id)
            """
            clauses_sql = self.db.adapt_sql(clauses_sql)
            clauses_sql = self.db.adapt_params(clauses_sql)
            cursor.execute(clauses_sql, (championship_id,))
            clauses_rows = cursor.fetchall()

            for row in clauses_rows:
                payer_id, receiver_id, clause_count, total_amount = row
                if payer_id in stats:
                    stats[payer_id]["clauses_paid"] += clause_count or 0
                    stats[payer_id]["total_clauses_paid"] += total_amount or 0
                if receiver_id in stats:
                    stats[receiver_id]["clauses_received"] += clause_count or 0
                    stats[receiver_id]["total_clauses_received"] += total_amount or 0

            transactions_sql = """
                SELECT 
                    buyer_team_id,
                    seller_team_id,
                    price
                FROM transactions
                WHERE championship_id = ?
            """
            transactions_sql = self.db.adapt_sql(transactions_sql)
            transactions_sql = self.db.adapt_params(transactions_sql)
            cursor.execute(transactions_sql, (championship_id,))
            txn_rows = cursor.fetchall()

            for row in txn_rows:
                buyer_team_id, seller_team_id, price = row
                if buyer_team_id in stats:
                    stats[buyer_team_id]["transaction_count"] += 1
                    stats[buyer_team_id]["total_spent"] += price or 0
                    stats[buyer_team_id]["transaction_profit"] -= price or 0
                if seller_team_id in stats:
                    stats[seller_team_id]["transaction_count"] += 1
                    stats[seller_team_id]["total_received"] += price or 0
                    stats[seller_team_id]["transaction_profit"] += price or 0

            # Normalize team_name and username fallbacks
            for team_id, entry in stats.items():
                if not entry["team_name"]:
                    team_info = self.dm.get_team_by_id(team_id)
                    if team_info and team_info.get("team_name"):
                        entry["team_name"] = team_info["team_name"]
                if not entry.get("username") and entry.get("user_id"):
                    user_info = self.get_user_by_id(entry["user_id"])
                    if user_info and user_info.get("username"):
                        entry["username"] = user_info["username"]

            return list(stats.values())

    def get_all_users_with_points(self, championship_id: str) -> List[Dict]:
        """Get all users/teams with their total points from team standings"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            # Get the latest matchday for each team to get their current total points
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    SELECT DISTINCT ON (ts.team_id)
                        ts.team_id,
                        t.team_name,
                        t.user_id,
                        u.username,
                        ts.points as total_points
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    LEFT JOIN users u ON t.user_id = u.user_id
                    WHERE ts.championship_id = %s
                    ORDER BY ts.team_id, ts.matchday DESC
                """
            else:
                sql = """
                    SELECT 
                        ts.team_id,
                        t.team_name,
                        t.user_id,
                        u.username,
                        ts.points as total_points
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    LEFT JOIN users u ON t.user_id = u.user_id
                    WHERE ts.championship_id = ? 
                    AND ts.matchday = (
                        SELECT MAX(matchday) 
                        FROM team_standings 
                        WHERE championship_id = ? AND team_id = ts.team_id
                    )
                    ORDER BY ts.points DESC
                """

            if self.db.db_type in ["postgresql", "postgres"]:
                cursor.execute(sql, (championship_id,))
            else:
                cursor.execute(sql, (championship_id, championship_id))

            results = cursor.fetchall()

            users = []
            for row in results:
                users.append(
                    {
                        "team_id": row[0],
                        "team_name": row[1],
                        "user_id": row[2],
                        "username": row[3] if row[3] else row[1],
                        "total_points": row[4] if row[4] else 0,
                    }
                )

            return users

    def get_evolution_data_from_db(self, championship_id: str) -> Dict:
        """Get evolution data (points and positions per matchday) from database

        Returns:
            Dict with structure:
            {
                "matchdays": [1, 2, 3, ...],
                "teams": [
                    {
                        "team_id": "...",
                        "team_name": "...",
                        "points_evolution": [40, 70, 100, ...],
                        "positions_evolution": [1, 2, 1, ...]
                    }
                ]
            }
        """
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            # Get all team standings ordered by matchday
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    SELECT 
                        ts.team_id,
                        t.team_name,
                        ts.matchday,
                        ts.points,
                        ts.position
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    WHERE ts.championship_id = %s
                    ORDER BY ts.matchday ASC, ts.position ASC
                """
            else:
                sql = """
                    SELECT 
                        ts.team_id,
                        t.team_name,
                        ts.matchday,
                        ts.points,
                        ts.position
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    WHERE ts.championship_id = ?
                    ORDER BY ts.matchday ASC, ts.position ASC
                """

            cursor.execute(sql, (championship_id,))
            results = cursor.fetchall()

            # Organize data by team
            teams_data = {}
            matchdays_set = set()

            for row in results:
                team_id = row[0]
                team_name = row[1]
                matchday = row[2]
                points = row[3]
                position = row[4]

                matchdays_set.add(matchday)

                if team_id not in teams_data:
                    teams_data[team_id] = {
                        "team_id": team_id,
                        "team_name": team_name,
                        "points_evolution": [],
                        "positions_evolution": [],
                    }

                teams_data[team_id]["points_evolution"].append(points)
                teams_data[team_id]["positions_evolution"].append(position)

            matchdays = sorted(matchdays_set)

            # Ensure all teams have data for all matchdays (fill with last known value)
            for team_id, team_data in teams_data.items():
                points_evol = team_data["points_evolution"]
                positions_evol = team_data["positions_evolution"]

                # Fill missing matchdays with last known value
                last_points = points_evol[-1] if points_evol else 0
                last_position = positions_evol[-1] if positions_evol else 0

                for i, md in enumerate(matchdays):
                    if i >= len(points_evol):
                        points_evol.append(last_points)
                        positions_evol.append(last_position)
                    else:
                        last_points = points_evol[i]
                        last_position = positions_evol[i]

            return {"matchdays": matchdays, "teams": list(teams_data.values())}

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        if not user_id:
            return None

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = "SELECT user_id, username FROM users WHERE user_id = ?"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()

        if not row:
            return None

        return {"user_id": row[0], "username": row[1]}
