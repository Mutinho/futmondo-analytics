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
