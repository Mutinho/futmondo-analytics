"""Infrastructure adapter implementing :class:`PrizesSyncDataPort` (BR2.2).

This is the ONLY module in the ``prizes`` sync context that touches the raw
``get_db()`` connection (the championship prize-config SELECT) and the atomic
``team_prizes`` writer. The config SELECT is moved here VERBATIM from the former
inline ``sync_prizes`` (not rewritten, not moved into ``data_manager_v2.py``), and
``replace_team_prizes`` delegates to the existing
``prizes.team_prizes_writer.replace_team_prizes`` UNCHANGED (NFR2, BR5.1).

The ``db`` handle is resolved lazily via ``get_db()`` on first use, exactly as the
former inline code did (``from app.services.db_connection import get_db`` inside
the method). A ``db`` may be injected for tests (the in-memory ``_FakeInMemoryDB``
honours the same contract).
"""

from typing import Iterable, Optional, Sequence, Tuple

from app.services.prizes.team_prizes_writer import replace_team_prizes


class DataManagerPrizesAdapter:
    """Adapt the raw ``get_db()`` config SELECT and the atomic writer to the port."""

    def __init__(self, db=None) -> None:
        """Create the adapter.

        Args:
            db: A ``DBConnection``-like handle. Defaults to lazy ``get_db()`` on
                first use, preserving the historical behavior (the former inline
                code imported and called ``get_db()`` inside ``sync_prizes``).
        """
        self._db = db

    @property
    def db(self):
        # Lazy resolution mirrors the former inline ``get_db()`` call site.
        if self._db is None:
            from app.services.db_connection import get_db

            self._db = get_db()
        return self._db

    def get_prize_config(self, championship_id: str) -> Optional[Tuple]:
        # Raw SELECT moved VERBATIM from the former inline sync_prizes (BR2.2).
        db = self.db
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            sql = "SELECT money_per_ranking, mvp_bonus, ranking_mode, users_to_rank, money_per_point, dream_team_bonus FROM user_championships WHERE championship_id = ? LIMIT 1"
            sql = db.adapt_params(sql)
            cursor.execute(sql, (championship_id,))
            return cursor.fetchone()

    def replace_team_prizes(
        self,
        championship_id: str,
        rows: Iterable[Sequence[object]],
        valid_matchdays: Iterable[int],
    ) -> int:
        # Delegated UNCHANGED to the atomic writer (NFR2, BR5.1): a failure
        # propagates so the write-point failure stays fatal (no mixed state).
        return replace_team_prizes(self.db, championship_id, rows, valid_matchdays)
