"""Infrastructure adapter for ``prizes`` reads — the only module with SQL (BR1.3).

Hosts the raw SQL formerly inline in ``DataManagerV2.get_prizes_by_team``, moved
**verbatim** (BR1.2/FR1.4). ``team_prizes`` is the single source of truth,
populated by ``DataSyncService.sync_prizes()`` which is untouched; this adapter
only reads it.
"""

from typing import Any, Dict, Optional

from app.services.data_manager.prizes.domain.ports import PrizesReadDataPort


class PrizesReadAdapter(PrizesReadDataPort):
    """Adapt the prize-read SQL (verbatim) to the port."""

    def __init__(self, dm: Optional[Any] = None) -> None:
        if dm is None:
            from app.services.data_manager_v2 import DataManagerV2

            dm = DataManagerV2(skip_init=True)
        self.dm = dm

    @property
    def db(self):
        return self.dm.db

    def get_prizes_by_team(self, championship_id: str) -> Dict[str, Dict[str, int]]:
        """Return accumulated prizes per team_id from the team_prizes table.

        team_prizes is the single source of truth for all prize money. It is
        populated by DataSyncService.sync_prizes(), which already enforces the
        business rules (a round only awards ranking/MVP/dream-team prizes once
        every match of the round has been played).

        Returns a mapping team_id -> {ranking, mvp, points, dream_team, total}.
        Teams with no prize rows are simply absent from the mapping.
        """
        prizes: Dict[str, Dict[str, int]] = {}
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = self.db.adapt_params("""
                SELECT
                    team_id,
                    COALESCE(SUM(ranking_prize), 0)    AS ranking,
                    COALESCE(SUM(mvp_prize), 0)        AS mvp,
                    COALESCE(SUM(points_prize), 0)     AS points,
                    COALESCE(SUM(dream_team_prize), 0) AS dream_team
                FROM team_prizes
                WHERE championship_id = ?
                GROUP BY team_id
            """)
            cursor.execute(sql, (championship_id,))
            for row in cursor.fetchall():
                team_id = row[0]
                ranking = int(row[1] or 0)
                mvp = int(row[2] or 0)
                points = int(row[3] or 0)
                dream_team = int(row[4] or 0)
                prizes[team_id] = {
                    "ranking": ranking,
                    "mvp": mvp,
                    "points": points,
                    "dream_team": dream_team,
                    "total": ranking + mvp + points + dream_team,
                }
        return prizes
