"""Infrastructure adapter for ``dream-teams-mvp`` — the only module with SQL (BR1.3).

Hosts the raw SQL formerly inline in ``DataManagerV2.save_dream_team_mvp`` /
``get_dream_team_bonus_stats``, moved **verbatim** including the engine branch
(BR1.2/FR1.4) and the legacy broad ``except`` path (BR3.2). Cross-responsibility
helpers (``ensure_championship_exists``, ``save_player``) are reached live via
``self.dm`` so production behavior is byte-for-byte identical (BR3.1).
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.data_manager.dream_teams_mvp.domain.ports import DreamTeamsMvpDataPort

logger = logging.getLogger(__name__)


class DreamTeamsMvpAdapter(DreamTeamsMvpDataPort):
    """Adapt the dream-team/MVP SQL (verbatim) to the port."""

    def __init__(self, dm: Optional[Any] = None) -> None:
        if dm is None:
            from app.services.data_manager_v2 import DataManagerV2

            dm = DataManagerV2(skip_init=True)
        self.dm = dm

    @property
    def db(self):
        return self.dm.db

    def save_dream_team_mvp(
        self,
        championship_id: str,
        round_id: str,
        matchday: int,
        dream_team_players: List[str],
        mvp_player_id: Optional[str] = None,
        player_details: Optional[Dict[str, Dict]] = None,
    ) -> None:
        """Save dream team and MVP for a specific round

        Args:
            championship_id: Championship ID
            round_id: Round ID
            matchday: Matchday number
            dream_team_players: List of player IDs in dream team
            mvp_player_id: Player ID of MVP (optional)
        """
        if not dream_team_players and not mvp_player_id:
            return

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            # Ensure championship exists in the same transaction
            self.dm.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)

            player_details = player_details or {}

            def player_exists(player_id: str) -> bool:
                if not player_id:
                    return False
                if self.db.db_type in ["postgresql", "postgres"]:
                    check_sql = "SELECT 1 FROM players WHERE player_id = %s"
                else:
                    check_sql = "SELECT 1 FROM players WHERE player_id = ?"
                    check_sql = self.db.adapt_params(check_sql)
                cursor.execute(check_sql, (player_id,))
                return cursor.fetchone() is not None

            def ensure_player(player_id: str) -> bool:
                if player_exists(player_id):
                    return True
                details = player_details.get(player_id)
                if not details:
                    return False
                payload = {
                    "id": details.get("id") or details.get("_id") or player_id,
                    "name": details.get("name", ""),
                    "role": details.get("role") or details.get("position", ""),
                    "teamId": details.get("teamId")
                    or details.get("team_id")
                    or details.get("teamId"),
                    "team": details.get("team") or details.get("teamName", ""),
                    "slug": details.get("slug", ""),
                    "photo_url": details.get("photo") or details.get("photo_url", ""),
                }
                try:
                    self.dm.save_player(payload)
                    return player_exists(player_id)
                except Exception as e:
                    logger.warning("Could not upsert player %s for dream team: %s", player_id, e)
                    return False

            # Save dream team players
            for player_id in dream_team_players:
                if not player_id:
                    continue
                if not ensure_player(player_id):
                    logger.warning(
                        "Skipping dream team player %s for round %s: not found in players table",
                        player_id,
                        round_id,
                    )
                    continue

                if self.db.db_type in ["postgresql", "postgres"]:
                    sql = """
                        INSERT INTO dream_teams_mvps 
                        (championship_id, round_id, matchday, player_id, is_mvp, recorded_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (championship_id, round_id, player_id, is_mvp) DO NOTHING
                    """
                else:
                    sql = """
                        INSERT OR IGNORE INTO dream_teams_mvps 
                        (championship_id, round_id, matchday, player_id, is_mvp, recorded_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """
                    sql = self.db.adapt_params(sql)

                cursor.execute(
                    sql,
                    (
                        championship_id,
                        round_id,
                        matchday,
                        player_id,
                        False,  # is_mvp
                        datetime.now(),
                    ),
                )

            # Save MVP if provided
            if mvp_player_id:
                if not ensure_player(mvp_player_id):
                    logger.warning(
                        "Skipping MVP %s for round %s: not found in players table",
                        mvp_player_id,
                        round_id,
                    )
                    mvp_player_id = None

            if mvp_player_id:
                if self.db.db_type in ["postgresql", "postgres"]:
                    sql = """
                        INSERT INTO dream_teams_mvps 
                        (championship_id, round_id, matchday, player_id, is_mvp, recorded_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (championship_id, round_id, player_id, is_mvp) DO NOTHING
                    """
                else:
                    sql = """
                        INSERT OR IGNORE INTO dream_teams_mvps 
                        (championship_id, round_id, matchday, player_id, is_mvp, recorded_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """
                    sql = self.db.adapt_params(sql)

                cursor.execute(
                    sql,
                    (
                        championship_id,
                        round_id,
                        matchday,
                        mvp_player_id,
                        True,  # is_mvp
                        datetime.now(),
                    ),
                )

            conn.commit()
            logger.info(
                f"Saved dream team/MVP for round {round_id} (matchday {matchday}): {len(dream_team_players)} players, MVP: {mvp_player_id or 'None'}"
            )

    def get_dream_team_bonus_stats(self, championship_id: str) -> Dict[str, Dict[str, int]]:
        """Return counts of dream-team appearances and MVP awards per team."""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    SELECT tr.team_id,
                           SUM(CASE WHEN dt.is_mvp THEN 0 ELSE 1 END) AS ideal_team_count,
                           SUM(CASE WHEN dt.is_mvp THEN 1 ELSE 0 END) AS mvp_count
                    FROM dream_teams_mvps dt
                    JOIN team_rosters tr
                      ON dt.championship_id = tr.championship_id
                     AND dt.matchday = tr.matchday
                     AND dt.player_id = tr.player_id
                    WHERE dt.championship_id = %s
                    GROUP BY tr.team_id
                """
                params = (championship_id,)
            else:
                sql = """
                    SELECT tr.team_id,
                           SUM(CASE WHEN dt.is_mvp THEN 0 ELSE 1 END) AS ideal_team_count,
                           SUM(CASE WHEN dt.is_mvp THEN 1 ELSE 0 END) AS mvp_count
                    FROM dream_teams_mvps dt
                    JOIN team_rosters tr
                      ON dt.championship_id = tr.championship_id
                     AND dt.matchday = tr.matchday
                     AND dt.player_id = tr.player_id
                    WHERE dt.championship_id = ?
                    GROUP BY tr.team_id
                """
                sql = self.db.adapt_params(sql)
                params = (championship_id,)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            bonus_map: Dict[str, Dict[str, int]] = {}
            for row in rows:
                team_id = row[0]
                ideal_count = row[1] or 0
                mvp_count = row[2] or 0
                bonus_map[team_id] = {
                    "ideal_team_count": ideal_count,
                    "mvp_count": mvp_count,
                }

            return bonus_map
