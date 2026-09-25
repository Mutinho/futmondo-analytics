"""Effect spec — atomic ``team_prizes`` replacement (u2-integrations, NFR2/BR5.1/BR5.2).

Q1 floor: the failure spec asserts the EFFECT (the table stays consistent), never
a bare ``pytest.raises``. It forces a failure INSIDE the replacement transaction
and asserts the previous consistent set survives intact (all-or-nothing), then it
asserts the happy path replaces the set and clears stale rows in one transaction.

Uses the shared in-memory ``fake_db`` (SQLite ``:memory:``) from ``conftest.py``,
which honours the ``db_connection`` contract (commit on success, rollback +
re-raise on any exception). No network, no real DB, no real credentials.
"""

import pytest

from app.services.prizes.team_prizes_writer import replace_team_prizes

_CID = "champ-1"


def _create_table(db):
    with db.get_connection() as conn:
        cur = db.get_cursor(conn)
        cur.execute(
            "CREATE TABLE team_prizes ("
            "championship_id TEXT, team_id TEXT, matchday INTEGER, "
            "ranking_prize REAL, mvp_prize REAL, position INTEGER, "
            "points_prize REAL, dream_team_prize REAL, synced_at TEXT, "
            "PRIMARY KEY (championship_id, team_id, matchday))"
        )
        # SQLite has no NOW(); the writer SQL uses NOW(). Provide it as a no-op-ish
        # function returning a fixed ISO string so the shared SQL runs unchanged.
        conn.create_function("NOW", 0, lambda: "2026-01-01T00:00:00")


def _matchdays(db):
    with db.get_connection() as conn:
        cur = db.get_cursor(conn)
        cur.execute(
            "SELECT matchday FROM team_prizes WHERE championship_id = ? ORDER BY matchday",
            (_CID,),
        )
        return [r[0] for r in cur.fetchall()]


def _seed(db, matchdays):
    with db.get_connection() as conn:
        cur = db.get_cursor(conn)
        for md in matchdays:
            cur.execute(
                "INSERT INTO team_prizes (championship_id, team_id, matchday, "
                "ranking_prize, mvp_prize, position, points_prize, dream_team_prize, "
                "synced_at) VALUES (?, 't1', ?, 0, 0, 1, 0, 0, '2026-01-01T00:00:00')",
                (_CID, md),
            )


def _row(matchday):
    # championship_id, team_id, matchday, ranking, mvp, position, points, dream
    return (_CID, "t1", matchday, 10.0, 0.0, 1, 5.0, 0.0)


# --- Characterization-first (Step 5): freeze the legacy mixed-state defect -----


def test_legacy_two_step_write_leaves_mixed_state_when_cleanup_fails():
    """FROZEN legacy defect the atomic writer removes (characterization-first).

    Reproduces the legacy pattern that lived inline in the god-file: a committed
    INSERT (new matchday 2), then a SEPARATE cleanup DELETE that fails and was
    swallowed by ``except cleanup_err: logger.warning``. The observable result is
    a MIXED state — the stale matchday 1 survives alongside the new matchday 2,
    and no exception reaches the caller. The atomic writer replaces this.
    """
    import sqlite3

    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE team_prizes (championship_id TEXT, team_id TEXT, matchday INTEGER, "
        "PRIMARY KEY (championship_id, team_id, matchday))"
    )
    conn.execute("INSERT INTO team_prizes VALUES ('c1', 't1', 1)")  # stale set
    conn.commit()

    # Step 1 (legacy): insert new matchday 2 and COMMIT immediately.
    conn.execute("INSERT INTO team_prizes VALUES ('c1', 't1', 2)")
    conn.commit()

    # Step 2 (legacy): separate cleanup DELETE that fails; legacy swallowed it.
    cleanup_failed = False
    try:
        conn.execute("DELETE FROM team_prizes WHERE this_column_does_not_exist = 1")
        conn.commit()
    except sqlite3.OperationalError:
        cleanup_failed = True

    assert cleanup_failed
    rows = [
        r[0]
        for r in conn.execute(
            "SELECT matchday FROM team_prizes WHERE championship_id = 'c1' ORDER BY matchday"
        ).fetchall()
    ]
    conn.close()
    assert rows == [1, 2], "legacy pattern leaves both stale and new row (mixed state)"


def test_db_context_manager_is_all_or_nothing(fake_db):
    """Contract the writer relies on: an exception in the ``with`` block rolls
    back every write in that block and re-raises (db_connection contract)."""
    _create_table(fake_db)
    _seed(fake_db, [1])
    assert _matchdays(fake_db) == [1]

    with pytest.raises(RuntimeError):
        with fake_db.get_connection() as conn:
            cur = fake_db.get_cursor(conn)
            cur.execute(
                "INSERT INTO team_prizes (championship_id, team_id, matchday, "
                "ranking_prize, mvp_prize, position, points_prize, dream_team_prize, "
                "synced_at) VALUES ('champ-1', 't1', 2, 0, 0, 1, 0, 0, 'x')"
            )
            raise RuntimeError("boom inside the transaction")

    assert _matchdays(fake_db) == [1]


# --- Atomic replacement effect specs (Step 5 hardening + Step 6) ---------------


def test_happy_path_replaces_set_and_clears_stale_in_one_transaction(fake_db):
    _create_table(fake_db)
    # Previous set: stale matchday 1 that must be removed.
    _seed(fake_db, [1])
    assert _matchdays(fake_db) == [1]

    # Replace with matchdays 2 and 3; valid = {2, 3} -> stale 1 must be deleted.
    stale_deleted = replace_team_prizes(
        fake_db, _CID, [_row(2), _row(3)], valid_matchdays={2, 3}
    )

    assert stale_deleted == 1
    assert _matchdays(fake_db) == [2, 3]


def test_failure_inside_transaction_leaves_previous_set_intact(fake_db):
    """EFFECT (BR5.1/BR5.2): a failure inside the replacement rolls back fully.

    The previous consistent set (matchday 1) must remain untouched — never a
    mixed state where the new rows landed but the stale row survived, or vice
    versa.
    """
    _create_table(fake_db)
    _seed(fake_db, [1])
    assert _matchdays(fake_db) == [1]

    # A row with the wrong arity forces cursor.execute to raise INSIDE the single
    # transaction (models any DB error at write time). The context manager must
    # roll the whole thing back and re-raise (not swallow).
    bad_row = (_CID, "t1", 2)  # too few columns for the INSERT

    with pytest.raises(Exception):
        replace_team_prizes(fake_db, _CID, [bad_row], valid_matchdays={2})

    # ALL-OR-NOTHING: the previous set is intact; nothing half-written.
    assert _matchdays(fake_db) == [1]


def test_delete_failure_rolls_back_the_upserts_too(fake_db):
    """A failure at the DELETE stage rolls back the upserts in the SAME txn.

    Drops the table between building rows and the delete? No — instead we force
    the DELETE to fail by making NOW unavailable is not it; we assert the
    combined guarantee via a valid upsert followed by a delete that references a
    non-existent column, all in one call.
    """
    _create_table(fake_db)
    _seed(fake_db, [1])

    # Monkeypatch adapt_params to inject a broken DELETE only (leave upsert SQL
    # intact) so the failure happens after the upserts, inside the same txn.
    original_adapt = fake_db.adapt_params

    def _adapt(sql):
        if sql.startswith("DELETE FROM team_prizes"):
            return "DELETE FROM team_prizes WHERE nonexistent_col = 1"
        return original_adapt(sql)

    fake_db.adapt_params = _adapt

    with pytest.raises(Exception):
        replace_team_prizes(fake_db, _CID, [_row(2)], valid_matchdays={2})

    fake_db.adapt_params = original_adapt
    # The upsert of matchday 2 must have rolled back with the failed DELETE:
    # only the previous set (matchday 1) survives — no mixed state.
    assert _matchdays(fake_db) == [1]
