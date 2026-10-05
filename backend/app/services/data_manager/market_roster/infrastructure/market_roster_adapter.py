"""Infrastructure adapter for ``market-roster`` — the only module with SQL (BR1.3).

Hosts the raw SQL formerly inline in ``DataManagerV2.save_market_players`` /
``save_team_roster`` / ``get_free_agent_candidates``, moved **verbatim**
including the engine branch (BR1.2/FR1.4). ``ensure_championship_exists`` is
reached live via ``self.dm`` so production behavior is byte-for-byte identical
(BR3.1).
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.data_manager.market_roster.domain.ports import MarketRosterDataPort

logger = logging.getLogger(__name__)


class MarketRosterAdapter(MarketRosterDataPort):
    """Adapt the market/roster SQL (verbatim) to the port."""

    def __init__(self, dm: Optional[Any] = None) -> None:
        if dm is None:
            from app.services.data_manager_v2 import DataManagerV2

            dm = DataManagerV2(skip_init=True)
        self.dm = dm

    @property
    def db(self):
        return self.dm.db

    def save_market_players(self, championship_id: str, players: List[Dict], matchday: int = None):
        """Save market players data with historical tracking"""
        if matchday is None:
            # Try to get current matchday
            matchday = 1  # Default

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            # Ensure championship exists in the same transaction
            self.dm.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)

            now = datetime.now()

            for player in players:
                player_id = player.get("id", "")
                if not player_id:
                    continue

                market_price = player.get(
                    "marketPrice", player.get("price", player.get("market_price"))
                )
                availability = player.get("availability", player.get("available", "unknown"))
                market_statistics = json.dumps(
                    player.get("marketStats", player.get("statistics", {}))
                )

                sql = """
                    INSERT INTO player_market_data 
                    (championship_id, player_id, matchday, market_price, availability, market_statistics, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                sql = self.db.adapt_params(sql)

                if self.db.db_type in ["postgresql", "postgres"]:
                    sql = """
                        INSERT INTO player_market_data 
                        (championship_id, player_id, matchday, market_price, availability, market_statistics, recorded_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (championship_id, player_id, matchday) DO UPDATE SET
                            market_price = EXCLUDED.market_price,
                            availability = EXCLUDED.availability,
                            market_statistics = EXCLUDED.market_statistics,
                            recorded_at = EXCLUDED.recorded_at
                    """
                else:
                    sql = """
                        INSERT OR REPLACE INTO player_market_data 
                        (championship_id, player_id, matchday, market_price, availability, market_statistics, recorded_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """
                    sql = self.db.adapt_params(sql)

                cursor.execute(
                    sql,
                    (
                        championship_id,
                        player_id,
                        matchday,
                        market_price,
                        availability,
                        market_statistics,
                        now,
                    ),
                )

        logger.info(f"Saved {len(players)} market players for matchday {matchday}")

    def save_team_roster(
        self, championship_id: str, team_id: str, players: List[Dict], matchday: int = None
    ):
        """Save team roster with historical tracking

        Also ensures the team exists in the teams table.
        """
        if matchday is None:
            matchday = 1  # Default

        # Ensure championship exists before inserting
        self.dm.ensure_championship_exists(championship_id)

        # Ensure team exists in teams table (create if not exists)
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            # Check if team exists
            sql = "SELECT team_id FROM teams WHERE team_id = ?"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (team_id,))
            team_exists = cursor.fetchone()

            if not team_exists:
                # Create team entry (we don't have name/user_id here, but that's OK)
                sql = "INSERT INTO teams (team_id, team_name, user_id) VALUES (?, ?, ?)"
                sql = self.db.adapt_params(sql)
                if self.db.db_type in ["postgresql", "postgres"]:
                    sql = """
                        INSERT INTO teams (team_id, team_name, user_id) 
                        VALUES (%s, %s, %s)
                        ON CONFLICT (team_id) DO NOTHING
                    """
                else:
                    sql = (
                        "INSERT OR IGNORE INTO teams (team_id, team_name, user_id) VALUES (?, ?, ?)"
                    )
                    sql = self.db.adapt_params(sql)

                cursor.execute(sql, (team_id, None, team_id))  # Use team_id as user_id fallback
                conn.commit()

        # Now save the roster
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            # Ensure championship exists in the same transaction
            self.dm.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)

            now = datetime.now()

            for idx, player in enumerate(players):
                player_id = player.get("id", "")
                if not player_id:
                    continue

                formation_position = player.get("position", player.get("formationPosition", ""))
                is_starter = player.get("isStarter", player.get("starter", True))
                lineup_order = player.get("lineupOrder", player.get("order", idx))

                sql = """
                    INSERT INTO team_rosters 
                    (championship_id, team_id, player_id, matchday, formation_position, is_starter, lineup_order, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                sql = self.db.adapt_params(sql)

                if self.db.db_type in ["postgresql", "postgres"]:
                    sql = """
                        INSERT INTO team_rosters 
                        (championship_id, team_id, player_id, matchday, formation_position, is_starter, lineup_order, recorded_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (championship_id, team_id, player_id, matchday) DO UPDATE SET
                            formation_position = EXCLUDED.formation_position,
                            is_starter = EXCLUDED.is_starter,
                            lineup_order = EXCLUDED.lineup_order,
                            recorded_at = EXCLUDED.recorded_at
                    """
                else:
                    sql = """
                        INSERT OR REPLACE INTO team_rosters 
                        (championship_id, team_id, player_id, matchday, formation_position, is_starter, lineup_order, recorded_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    sql = self.db.adapt_params(sql)

                cursor.execute(
                    sql,
                    (
                        championship_id,
                        team_id,
                        player_id,
                        matchday,
                        formation_position,
                        is_starter,
                        lineup_order,
                        now,
                    ),
                )

            # Commit the transaction
            conn.commit()

        logger.info(
            f"Saved roster for team {team_id} (matchday {matchday}): {len(players)} players"
        )

    def get_free_agent_candidates(self, championship_id: str) -> List[Dict]:
        """Return players without owner based on player_championship_stats"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = """
                SELECT pcs.player_id, p.name, pcs.clause_price, pcs.suggested_clause,
                       pcs.average_last_five, pcs.average_overall
                FROM player_championship_stats pcs
                LEFT JOIN players p ON p.player_id = pcs.player_id
                WHERE pcs.championship_id = ? AND (pcs.owner_team_id IS NULL OR pcs.owner_team_id = '')
            """
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (championship_id,))
            rows = cursor.fetchall()

        players = []
        for row in rows:
            players.append(
                {
                    "player_id": row[0],
                    "name": row[1],
                    "clause_price": row[2],
                    "suggested_clause": row[3],
                    "average_last_five": row[4],
                    "average_overall": row[5],
                }
            )
        return players
