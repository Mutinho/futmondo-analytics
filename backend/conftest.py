"""
Fixtures compartidas para la suite de caracterización (red de seguridad).

Estos tests congelan el comportamiento ACTUAL del código existente antes de
refactorizarlo (metodología `custom`, characterization-first — ver Testing
Contract del plan). No usan BD real: se inyectan fakes de `DataManager`/conexión
por fixture (patrón de `test_analytics_service.py`) y factories/fakes para las
APIs externas. Nunca se copian datos ni credenciales reales a los tests.
"""

import os
import sys

import pytest

# Asegura que `from app...` resuelve al ejecutar desde backend/ (R-01). pytest.ini
# ya fija pythonpath = . ; esto lo hace robusto si se invoca de otra forma.
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)


@pytest.fixture
def clean_jwt_env(monkeypatch):
    """Aísla las variables de entorno que gobiernan el arranque JWT/servicio.

    Cada test que ejercita `app.core.config` debe partir de un entorno conocido
    para no depender del `.env` de la máquina de desarrollo.
    """
    for var in ("JWT_SECRET", "FLY_APP_NAME"):
        monkeypatch.delenv(var, raising=False)
    return monkeypatch


import sqlite3  # noqa: E402
from contextlib import contextmanager  # noqa: E402
from datetime import date, datetime  # noqa: E402


class _FakeInMemoryDB:
    """In-memory persistence fake honoring the ``db_connection`` contract.

    Backed by a single shared in-memory SQLite connection so it exercises the
    repositories' real parameterized SQL without touching Neon. Datetime params
    are ISO-encoded (SQLite has no native datetime binding), mirroring the
    Turso cursor wrapper in production. ``db_type`` is ``sqlite`` so repositories
    take the SQLite branch (no PostgreSQL-only ``FOR UPDATE`` suffix).
    """

    db_type = "sqlite"

    def __init__(self):
        self._conn = sqlite3.connect(":memory:")

    @contextmanager
    def get_connection(self):
        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def get_cursor(self, conn):
        return _FakeCursor(conn.cursor())

    def adapt_params(self, sql: str) -> str:
        # SQLite uses ? placeholders; SQL is already written with ?.
        return sql

    def close(self):
        self._conn.close()


class _FakeCursor:
    """Cursor wrapper that ISO-encodes datetime/date params for SQLite."""

    def __init__(self, cursor):
        self._cursor = cursor

    @staticmethod
    def _convert(params):
        if params is None:
            return None
        converted = []
        for p in params:
            if isinstance(p, (datetime, date)):
                converted.append(p.isoformat())
            else:
                converted.append(p)
        return tuple(converted)

    def execute(self, sql, params=None):
        if params is not None:
            return self._cursor.execute(sql, self._convert(params))
        return self._cursor.execute(sql)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    @property
    def rowcount(self):
        return self._cursor.rowcount


@pytest.fixture
def fake_db():
    """A fresh in-memory persistence fake per test (no shared mutable state)."""
    db = _FakeInMemoryDB()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _no_real_db_on_data_manager_construction(monkeypatch):
    """Prevent ``DataManagerV2()`` from opening a real PostgreSQL connection.

    ``DBConnection.__init__`` eagerly builds a psycopg2 pool and runs a
    ``SELECT 1;`` liveness probe, so ``DataManagerV2(skip_init=True)`` would hit
    a real database at construction time — before a test can reassign
    ``dm.db = fake_db``. The facade constructor also calls
    ``_ensure_schema_updates()`` eagerly against that connection. In CI (where no
    PostgreSQL runs, by design — the suite uses the in-memory fake, NFR6) that
    raised ``psycopg2.OperationalError`` for every characterization test that
    builds the facade.

    This autouse fixture makes ``DBConnection.__init__`` back its connection with
    an in-memory SQLite double (the same ``_FakeInMemoryDB`` the suite already
    uses), test-only and without touching production code: the eager
    ``_ensure_schema_updates`` on construction runs harmlessly against memory,
    and tests immediately reassign ``dm.db = fake_db`` for their own seeded
    schema. The characterized ``_ensure_schema_updates`` method is NOT stubbed —
    the schema-lifecycle test that calls it explicitly against its injected fake
    still exercises the real delegation. Tests that build a hollow
    ``DBConnection`` via ``__new__`` are unaffected (they never run ``__init__``).
    """
    from app.services.db_connection import DBConnection

    def _no_connect(self, *args, **kwargs):
        # Stable attributes real callers read; no pool, no network. Back the
        # connection surface with an in-memory SQLite fake so the facade's eager
        # construction-time schema hook runs against memory, never PostgreSQL.
        _backing = _FakeInMemoryDB()
        self.db_type = "postgresql"
        self._pool = None
        self.get_connection = _backing.get_connection
        self.get_cursor = _backing.get_cursor
        self.adapt_params = _backing.adapt_params
        self.adapt_sql = lambda sql: sql

    monkeypatch.setattr(DBConnection, "__init__", _no_connect, raising=True)
