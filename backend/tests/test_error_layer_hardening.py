"""Characterization + reclassification tests for the first-wave broad captures.

U1 `u1-error-layer`, Steps 4-5 (FR3.2.2, BR1.6). These specs freeze the
observable behaviour of the hardened captures and assert the EFFECT of the
recoverable/fatal classification — never a bare ``pytest.raises`` without a
state assertion (Q1):

- FATAL: ``_test_connection`` propagates a dead-DB error (fail fast/clean).
- FATAL: the transactional ``get_connection`` rolls back AND re-raises on error,
  leaving no committed partial data (NFR2) — pre-existing semantics preserved.
- RECOVERABLE: a pool-creation failure degrades to direct connections
  (``_pool = None``) and init continues.

In-memory doubles only: no network, no real DB, no credentials. The DBConnection
is built without ``__init__`` (which would open real connections), mirroring the
existing ``test_db_engine_characterization`` pattern.

Note (FR14.1): production now targets PostgreSQL/Neon only, so these specs
exercise the single remaining engine path. The recoverable/fatal semantics they
freeze are unchanged by the SQLite/Turso retirement — they moved with the code,
not away from it.
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import pytest  # noqa: E402

from app.services.db_connection import DBConnection  # noqa: E402


def _make_conn():
    """Build a DBConnection (PostgreSQL/Neon) without opening real connections."""
    conn = DBConnection.__new__(DBConnection)
    conn.db_type = "postgresql"
    conn.db_path = ":memory:"
    conn._pool = None
    conn.connection_string = "postgresql://x"
    return conn


# --- In-memory connection doubles (honour the get_connection contract) ---


class _RecordingConn:
    """A fake DB connection recording commit/rollback, optionally failing on use.

    ``fail_on_cursor_execute`` fails the ``SELECT 1`` liveness probe (inside the
    transaction block, so rollback runs). ``execute`` (the sqlite ``PRAGMA``)
    always succeeds so the sqlite branch reaches its ``try``/yield.
    """

    def __init__(self, fail_on_cursor_execute=False):
        self.committed = False
        self.rolled_back = False
        self._fail_on_cursor_execute = fail_on_cursor_execute

    def cursor(self):
        return _RecordingCursor(self)

    def execute(self, *_a, **_k):
        # sqlite PRAGMA journal_mode — must succeed to reach the try block.
        return None

    def _cursor_execute(self):
        if self._fail_on_cursor_execute:
            raise RuntimeError("db unreachable")

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        pass


class _RecordingCursor:
    def __init__(self, conn):
        self._conn = conn

    def execute(self, *_a, **_k):
        self._conn._cursor_execute()


class _Connector:
    """Stands in for sqlite3/psycopg2 connect()."""

    def __init__(self, conn):
        self._conn = conn

    def connect(self, *_a, **_k):
        return self._conn


# --- FATAL: _test_connection propagates a dead DB (fail fast) ---


def test_test_connection_propagates_on_dead_db_fatal():
    """A DB that fails the liveness probe is FATAL: the error propagates.

    Effect asserted: the exception is raised (not degraded to a warning) AND the
    failing connection was rolled back — no silent success.
    """
    conn = _make_conn()
    dead = _RecordingConn(fail_on_cursor_execute=True)
    conn.connector = _Connector(dead)

    with pytest.raises(RuntimeError, match="db unreachable"):
        conn._test_connection()

    # Effect: the transaction context rolled back the dead connection.
    assert dead.rolled_back is True
    assert dead.committed is False


def test_test_connection_succeeds_on_live_db():
    """Characterization: a live DB probe commits and does not raise."""
    conn = _make_conn()
    live = _RecordingConn(fail_on_cursor_execute=False)
    conn.connector = _Connector(live)

    conn._test_connection()  # must not raise

    assert live.committed is True
    assert live.rolled_back is False


# --- FATAL: transactional get_connection rolls back AND re-raises (NFR2) ---


def test_get_connection_rolls_back_and_raises_on_error_no_partial_commit():
    """A failure inside the transaction is FATAL: rollback()+raise, no commit.

    Effect asserted: the exception propagates, the connection was rolled back,
    and it was NEVER committed — so no half-written data survives (NFR2, BR1.5).
    """
    conn = _make_conn()
    tx_conn = _RecordingConn()
    conn.connector = _Connector(tx_conn)

    with pytest.raises(ValueError, match="boom"):
        with conn.get_connection() as c:
            assert c is tx_conn
            raise ValueError("boom")

    assert tx_conn.rolled_back is True
    assert tx_conn.committed is False


def test_get_connection_commits_on_success():
    """Characterization: the happy path commits and does not roll back."""
    conn = _make_conn()
    tx_conn = _RecordingConn()
    conn.connector = _Connector(tx_conn)

    with conn.get_connection() as c:
        assert c is tx_conn

    assert tx_conn.committed is True
    assert tx_conn.rolled_back is False


# --- RECOVERABLE: pool creation failure degrades to direct connections ---


def test_pool_creation_failure_degrades_to_direct_connections(monkeypatch):
    """A pool-creation failure is RECOVERABLE: fall back to direct connections.

    Effect asserted: ``_init_postgresql`` does NOT raise from the pool failure,
    ``_pool`` ends as ``None`` (direct-connection mode), and boot continues to
    the liveness probe (which here succeeds).
    """
    conn = _make_conn()
    live = _RecordingConn(fail_on_cursor_execute=False)

    class _FailingPoolModule:
        class pool:
            class ThreadedConnectionPool:
                def __init__(self, *_a, **_k):
                    raise RuntimeError("no pool for you")

        @staticmethod
        def connect(*_a, **_k):
            # Direct-connection fallback path uses connector.connect(...).
            return live

    # psycopg2 is imported inside _init_postgresql; inject fakes via sys.modules.
    import sys

    monkeypatch.setitem(sys.modules, "psycopg2", _FailingPoolModule)
    monkeypatch.setitem(sys.modules, "psycopg2.pool", _FailingPoolModule.pool)

    # Should degrade (not raise) and reach the successful liveness probe.
    conn._init_postgresql("postgresql://x")

    assert conn._pool is None  # recoverable: fell back to direct connections
    assert live.committed is True  # liveness probe ran and succeeded
