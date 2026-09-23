"""Migration error-handling contract for `init_auth_tables` (FR3.2 / BR5).

Freezes the narrowed exception handling of the migration loop after R-01:

- An EXPECTED "already exists" error (a duplicate column/object on a re-run) is
  swallowed and logged at debug — the migration is idempotent.
- ANY OTHER error raised while running a migration (bad SQL, undefined table,
  missing privileges, connection loss, or a generic ``psycopg2.ProgrammingError``)
  is FATAL and MUST re-propagate. Swallowing it would hide a real production
  migration failure on the PostgreSQL path (FR3.2 recoverable = log; fatal =
  re-raise; forbidden = swallow).

No network, no real DB: a fake ``db`` honoring the ``db_connection`` contract is
injected via ``get_db`` so the loop runs against controllable ``cursor.execute``
behavior. ``db_type = "sqlite"`` steers the CREATE branch to the SQLite path.
"""

import sqlite3
from contextlib import contextmanager

import pytest

from app.auth import token_store


class _FakeCursor:
    """Cursor whose ``execute`` raises on ALTER TABLE migration statements.

    CREATE TABLE statements (the setup phase) succeed silently; the injected
    error only fires for the migration loop's ``ALTER TABLE ... ADD COLUMN``
    statements, so the test isolates the loop's exception handling.
    """

    def __init__(self, exc):
        self._exc = exc

    def execute(self, sql, params=None):
        if sql.strip().upper().startswith("ALTER TABLE"):
            raise self._exc
        return None

    def commit(self):
        return None


class _FakeConn:
    def commit(self):
        return None

    def rollback(self):
        return None


class _FakeMigrationDB:
    """Fake DB whose migration statements raise a caller-supplied exception."""

    db_type = "sqlite"

    def __init__(self, exc):
        self._exc = exc

    @contextmanager
    def get_connection(self):
        conn = _FakeConn()
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise

    def get_cursor(self, conn):
        return _FakeCursor(self._exc)


def test_non_duplicate_migration_error_propagates(monkeypatch):
    """A NON-"already exists" error must NOT be swallowed (R-01 regression guard).

    Before the fix the loop caught the broad ``psycopg2.ProgrammingError``
    superclass. ``UndefinedTable`` — a FATAL migration error — is a subclass of
    that superclass, so the old code would have masked it. We inject exactly that
    error (when psycopg2 is importable, as it is in CI) so the test only passes
    once the catch is narrowed to ``DuplicateColumn``/``DuplicateObject``. On a
    psycopg2-less environment we fall back to a generic ``RuntimeError``, which
    the migration loop must never catch either.
    """
    try:
        from psycopg2 import errors as psycopg2_errors

        boom = psycopg2_errors.UndefinedTable(
            "relation \"user_championships\" does not exist"
        )
        expected_type = psycopg2_errors.UndefinedTable
        expected_match = "does not exist"
    except Exception:
        boom = RuntimeError("fatal migration failure in production")
        expected_type = RuntimeError
        expected_match = "fatal migration failure"

    monkeypatch.setattr(token_store, "get_db", lambda: _FakeMigrationDB(boom))

    with pytest.raises(expected_type, match=expected_match):
        token_store.init_auth_tables()


def test_generic_runtime_error_migration_propagates(monkeypatch):
    """A generic ``RuntimeError`` from a migration must reach the caller.

    psycopg2-independent floor for the "fatal = re-raise, never swallow" rule
    (FR3.2 / BR5): a ``RuntimeError`` is in no duplicate-errors tuple on any
    backend, so it must always propagate.
    """
    boom = RuntimeError("connection lost mid-migration")
    monkeypatch.setattr(token_store, "get_db", lambda: _FakeMigrationDB(boom))

    with pytest.raises(RuntimeError, match="connection lost"):
        token_store.init_auth_tables()


def test_duplicate_column_error_is_swallowed(monkeypatch):
    """An EXPECTED "already exists" error is benign and must NOT propagate.

    ``sqlite3.OperationalError`` is the SQLite member of the narrowed
    duplicate-errors tuple; raising it from the migration loop must be absorbed
    (idempotent re-run), so ``init_auth_tables`` returns normally.
    """
    already_exists = sqlite3.OperationalError("duplicate column name: is_pro")
    monkeypatch.setattr(
        token_store, "get_db", lambda: _FakeMigrationDB(already_exists)
    )

    # Must not raise: the expected duplicate is swallowed and logged at debug.
    token_store.init_auth_tables()
