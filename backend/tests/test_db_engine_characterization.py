"""
Tests de caracterización de la capa de acceso a datos MULTI-MOTOR (FR7.1, C4).

`DBConnection` abstrae SQLite, PostgreSQL y Turso. Este test congela la
SELECCIÓN de motor y la adaptación de placeholders/DDL SIN conectar a ninguna BD
real: se construye la instancia evitando el `__init__` (que abriría conexiones) y
se ejercitan los métodos puros de adaptación. Marca la capa antes de refactorizarla.
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

from app.services.db_connection import DBConnection  # noqa: E402


def _make_conn(db_type):
    """Crea un DBConnection con un db_type fijado, sin abrir conexiones reales."""
    conn = DBConnection.__new__(DBConnection)
    conn.db_type = db_type
    conn.db_path = ":memory:"
    conn._pool = None
    return conn


def test_adapt_params_postgres_converts_qmark_to_percent_s():
    conn = _make_conn("postgresql")
    assert conn.adapt_params("SELECT * FROM t WHERE id = ?") == \
        "SELECT * FROM t WHERE id = %s"


def test_adapt_params_sqlite_keeps_qmark():
    conn = _make_conn("sqlite")
    assert conn.adapt_params("SELECT * FROM t WHERE id = ?") == \
        "SELECT * FROM t WHERE id = ?"


def test_adapt_params_turso_keeps_qmark():
    """Turso es compatible SQLite: no se adaptan placeholders."""
    conn = _make_conn("turso")
    assert conn.adapt_params("SELECT * FROM t WHERE id = ?") == \
        "SELECT * FROM t WHERE id = ?"


def test_adapt_params_postgres_leaves_already_percent_s():
    conn = _make_conn("postgresql")
    assert conn.adapt_params("SELECT * FROM t WHERE id = %s") == \
        "SELECT * FROM t WHERE id = %s"


def test_adapt_sql_postgres_rewrites_autoincrement():
    conn = _make_conn("postgresql")
    out = conn.adapt_sql("id INTEGER PRIMARY KEY AUTOINCREMENT")
    assert "SERIAL PRIMARY KEY" in out
    assert "AUTOINCREMENT" not in out


def test_adapt_sql_sqlite_is_noop():
    conn = _make_conn("sqlite")
    sql = "id INTEGER PRIMARY KEY AUTOINCREMENT"
    assert conn.adapt_sql(sql) == sql


def test_get_cursor_wraps_turso_cursor_only():
    """Para Turso el cursor se envuelve (auto-conversión de datetime); para el
    resto se devuelve el cursor tal cual. Congela la selección por motor."""
    from app.services.db_connection import _TursoCursorWrapper

    class _RawCursor:
        pass

    class _Conn:
        def cursor(self):
            return _RawCursor()

    turso = _make_conn("turso")
    wrapped = turso.get_cursor(_Conn())
    assert isinstance(wrapped, _TursoCursorWrapper)

    sqlite = _make_conn("sqlite")
    raw = sqlite.get_cursor(_Conn())
    assert isinstance(raw, _RawCursor)
