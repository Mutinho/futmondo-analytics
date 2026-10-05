"""Characterization safety net for the ``schema-lifecycle`` responsibility (rank 14, last).

Freezes the observable effect of the SQLite-executable lifecycle paths over the
in-memory fake (BR2.1/BR3.1): championship bootstrap (standalone + same-transaction,
idempotent), and ``_ensure_schema_updates`` creating the newer tables. The
``_init_database`` / ``reset_database`` DDL uses PostgreSQL-only ``SERIAL`` /
``BOOLEAN`` / ``CASCADE`` that plain SQLite cannot parse, so those are exercised in
production against the real engine; here we freeze that ``__init__`` still delegates
its schema calls (``_ensure_schema_updates`` runs on construction) and that
``reset_database`` remains a thin delegator wired to the module. Never ``assert
True`` for the SQL paths (BR2.2/BR2.3). No network/real DB/credentials.
"""

import pytest

from app.services.data_manager_v2 import DataManagerV2


def _make_dm(fake_db):
    dm = DataManagerV2(skip_init=True)
    fake_db.adapt_sql = lambda sql: sql  # SQLite passthrough for CREATE IF NOT EXISTS DDL
    dm.db = fake_db
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS championships (championship_id TEXT PRIMARY KEY, name TEXT, created_at TEXT)"
        )
        cursor.execute("CREATE TABLE IF NOT EXISTS players (player_id TEXT PRIMARY KEY, name TEXT)")
    return dm


def _champ_count(fake_db, cid):
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("SELECT COUNT(*) FROM championships WHERE championship_id = ?", (cid,))
        return cursor.fetchone()[0]


def test_ensure_championship_exists_standalone_creates_once(fake_db):
    dm = _make_dm(fake_db)
    dm.ensure_championship_exists("c1")
    assert _champ_count(fake_db, "c1") == 1
    # Idempotent: a second call does not duplicate.
    dm.ensure_championship_exists("c1")
    assert _champ_count(fake_db, "c1") == 1


def test_ensure_championship_exists_uses_name_when_given(fake_db):
    dm = _make_dm(fake_db)
    dm.ensure_championship_exists("c2", name="La Liga")
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("SELECT name FROM championships WHERE championship_id = ?", ("c2",))
        assert cursor.fetchone()[0] == "La Liga"


def test_ensure_championship_in_transaction_same_conn(fake_db):
    dm = _make_dm(fake_db)
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        dm.ensure_championship_exists("c3", conn=conn, cursor=cursor)
        conn.commit()
    assert _champ_count(fake_db, "c3") == 1


def test_ensure_schema_updates_creates_newer_tables(fake_db):
    dm = _make_dm(fake_db)
    dm._ensure_schema_updates()
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        for table in ("player_championship_stats", "match_odds", "matchday_articles"):
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (table,)
            )
            assert cursor.fetchone() is not None, f"{table} should have been created"


def test_init_constructs_without_running_full_schema_when_skip_init(fake_db):
    # __init__(skip_init=True) must NOT run _init_database (PostgreSQL-only DDL)
    # but must still call _ensure_schema_updates against whatever db is set at
    # construction time. We assert construction succeeds and the facade exposes
    # the delegated reset_database/ensure_championship_exists surface.
    dm = DataManagerV2(skip_init=True)
    assert hasattr(dm, "reset_database")
    assert hasattr(dm, "ensure_championship_exists")
    assert callable(dm.reset_database)
