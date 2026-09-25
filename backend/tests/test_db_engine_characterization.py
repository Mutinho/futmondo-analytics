"""
Characterization tests for the PostgreSQL/Neon data-access layer (FR7.1, FR14.1.5).

After FR14.1 (limpieza de configuración), ``DBConnection`` targets a SINGLE
production engine: PostgreSQL/Neon via ``DATABASE_URL``. The removed SQLite and
Turso (LibSQL) production branches are dead code; this suite freezes the
placeholder/DDL adaptation and cursor-selection contract of the engine that
REMAINS, without connecting to any real database: the instance is built bypassing
``__init__`` (which would open connections) and only the pure adaptation methods
are exercised. Characterization-first: this file is updated in lockstep with the
Turso/SQLite retirement so the suite stays green (R-01/R-03).

Note on the in-memory test fake: ``conftest.py``'s ``_FakeInMemoryDB`` uses
``db_type="sqlite"`` and is INDEPENDENT of the production SQLite branch removed
here — it is a self-contained persistence double for repositories, not the
production connector. Removing the production SQLite/Turso branches does not
affect it.
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

from app.services.db_connection import DBConnection  # noqa: E402


def _make_conn(db_type):
    """Build a DBConnection with a fixed db_type, without opening real connections."""
    conn = DBConnection.__new__(DBConnection)
    conn.db_type = db_type
    conn.db_path = ":memory:"
    conn._pool = None
    return conn


def test_adapt_params_postgres_converts_qmark_to_percent_s():
    conn = _make_conn("postgresql")
    assert conn.adapt_params("SELECT * FROM t WHERE id = ?") == \
        "SELECT * FROM t WHERE id = %s"


def test_adapt_params_postgres_leaves_already_percent_s():
    conn = _make_conn("postgresql")
    assert conn.adapt_params("SELECT * FROM t WHERE id = %s") == \
        "SELECT * FROM t WHERE id = %s"


def test_adapt_params_postgres_leaves_parameterless_sql():
    """No placeholders means nothing to rewrite for the Neon path."""
    conn = _make_conn("postgresql")
    assert conn.adapt_params("SELECT 1") == "SELECT 1"


def test_adapt_sql_postgres_rewrites_autoincrement():
    conn = _make_conn("postgresql")
    out = conn.adapt_sql("id INTEGER PRIMARY KEY AUTOINCREMENT")
    assert "SERIAL PRIMARY KEY" in out
    assert "AUTOINCREMENT" not in out


def test_get_cursor_returns_raw_cursor_for_postgres():
    """After the Turso retirement, get_cursor always returns the raw DB cursor
    unchanged (no wrapper); this freezes the single-engine selection (R-03)."""
    class _RawCursor:
        pass

    class _Conn:
        def cursor(self):
            return _RawCursor()

    pg = _make_conn("postgresql")
    raw = pg.get_cursor(_Conn())
    assert isinstance(raw, _RawCursor)


def test_get_last_insert_id_postgres_reads_returning_row():
    """PostgreSQL/Neon returns the id via a RETURNING row (fetchone), not lastrowid."""
    class _CursorWithReturning:
        description = [("id",)]

        def fetchone(self):
            return (42,)

    conn = _make_conn("postgresql")
    assert conn.get_last_insert_id(_CursorWithReturning(), "players") == 42


def test_get_last_insert_id_postgres_none_without_description():
    """No RETURNING clause (no description) yields None on the Neon path."""
    class _CursorNoDescription:
        description = None

    conn = _make_conn("postgresql")
    assert conn.get_last_insert_id(_CursorNoDescription(), "players") is None
