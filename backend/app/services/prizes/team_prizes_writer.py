"""Atomic transactional replacement of the ``team_prizes`` cache — u2-integrations.

NFR2 / BR5.1 / BR5.2: the ``team_prizes`` set for a championship must be replaced
all-or-nothing. The previous implementation lived inside the ``data_sync_service``
god-file and split the write into (a) a per-round ``INSERT ... ON CONFLICT`` that
committed immediately and (b) a SEPARATE ``DELETE ... NOT IN (...)`` cleanup
transaction whose failure was swallowed by ``except cleanup_err: logger.warning``.
On a cleanup failure the table was left in a MIXED state: the new rows committed
but the stale rows never removed, and no signal reached the consumer.

This narrow, testable function fixes that (NFR2): the stale-row DELETE and the
full repopulate run in a SINGLE transaction. Any failure rolls the whole thing
back, so the previous consistent set stays intact — never a half-written state.
It lives OUTSIDE the god-file (no god-file expansion): ``sync_prizes`` computes
the rows and calls this function.

State machine (functional-design §3): ``STABLE -> IN_TXN -> (COMMITTED |
ROLLED_BACK) -> STABLE``.

Identifiers, docstrings and comments are in English (team Code Style). There is
no user-facing text here (internal persistence helper).
"""

import logging
from typing import Iterable, Protocol, Sequence

logger = logging.getLogger(__name__)


# The upsert of one team_prizes row (positional, matching the existing schema
# order): championship_id, team_id, matchday, ranking_prize, mvp_prize, position,
# points_prize, dream_team_prize.
TeamPrizeRow = Sequence[object]


class _DbLike(Protocol):
    """Structural type of the ``db_connection.DBConnection`` surface used here.

    Depending on the behaviour (not a concrete class) keeps this function
    testable with the in-memory ``_FakeInMemoryDB`` from ``conftest.py``, which
    honours the same contract (``get_connection`` context manager that commits on
    success and rolls back + re-raises on any exception).
    """

    def get_connection(self): ...

    def get_cursor(self, conn): ...

    def adapt_params(self, sql: str) -> str: ...


_UPSERT_SQL = (
    "INSERT INTO team_prizes (championship_id, team_id, matchday, ranking_prize, "
    "mvp_prize, position, points_prize, dream_team_prize, synced_at) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, NOW()) "
    "ON CONFLICT (championship_id, team_id, matchday) DO UPDATE SET "
    "ranking_prize = EXCLUDED.ranking_prize, mvp_prize = EXCLUDED.mvp_prize, "
    "position = EXCLUDED.position, points_prize = EXCLUDED.points_prize, "
    "dream_team_prize = EXCLUDED.dream_team_prize, synced_at = NOW()"
)


def replace_team_prizes(
    db: _DbLike,
    championship_id: str,
    rows: Iterable[TeamPrizeRow],
    valid_matchdays: Iterable[int],
) -> int:
    """Replace the ``team_prizes`` set for a championship atomically (BR5.1).

    In a SINGLE transaction: upsert every row in ``rows`` and delete the rows
    whose ``matchday`` is not in ``valid_matchdays`` (the stale-cleanup that used
    to be a separate, failure-swallowing transaction). If ANY step raises, the
    ``get_connection`` context manager rolls the whole transaction back and
    re-raises, so the previous consistent set survives intact (all-or-nothing).
    The failure is NOT swallowed: the caller (the sync capture point) classifies
    it (a write-point failure is fatal — BR2.3 / BR3.2).

    Args:
        db: A ``DBConnection``-like object (real or the in-memory test fake).
        championship_id: The championship whose prize set is being replaced.
        rows: The full set of team_prizes rows to persist (positional, in schema
            column order). May be empty (then only stale cleanup runs).
        valid_matchdays: The matchdays that must remain; every other matchday for
            this championship is deleted inside the same transaction.

    Returns:
        The number of stale rows deleted (``cursor.rowcount`` of the DELETE, or
        ``0`` when it is not reported).

    Raises:
        Exception: any DB error is propagated after the transaction rolls back
            (never swallowed), so no partial/mixed state can survive (NFR2).
    """
    rows = list(rows)
    valid = list(valid_matchdays)
    stale_deleted = 0

    # Single transaction: the context manager commits on success and rolls back +
    # re-raises on any exception (db_connection contract, honoured by the fake).
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)

        # 1) Repopulate (upsert) the full computed set.
        upsert_sql = db.adapt_params(_UPSERT_SQL)
        for row in rows:
            cursor.execute(upsert_sql, tuple(row))

        # 2) Delete stale rows for matchdays no longer valid — SAME transaction,
        #    so a failure here rolls back the upserts too (no mixed state).
        if valid:
            placeholders = ",".join(["?"] * len(valid))
            delete_sql = db.adapt_params(
                f"DELETE FROM team_prizes WHERE championship_id = ? "
                f"AND matchday NOT IN ({placeholders})"
            )
            cursor.execute(delete_sql, (championship_id, *valid))
            stale_deleted = cursor.rowcount if cursor.rowcount is not None else 0

    if stale_deleted:
        logger.info(
            "Removed %s stale prize rows for matchdays not in %s",
            stale_deleted,
            sorted(valid),
        )
    return stale_deleted
