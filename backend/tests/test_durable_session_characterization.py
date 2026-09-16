"""Characterization tests (safety net) for u1-durable-session.

These froze the CURRENT behavior of the code BEFORE the durability refactor.
They were a safety net, not TDD: the failing-behavior tests documented known
defects. Per team.md/the Testing Contract, the phase-1 tests that described a
FAILURE are updated/retired in a TRACEABLE way once the behavior changes on
purpose (plan Steps 8-10).

Traceable update log:
  (a)+(b) — Step 10 deliberately replaced the opaque HTTP 403 after a restart
      (and the docstring that promised a re-creation the code never did) with an
      actionable 401 backed by durable rehydration. The former "frozen failure"
      assertions (403 + contradictory docstring) are RETIRED and REPLACED below
      by the new-contract assertion, which lives authoritatively in
      ``test_durable_session_api.py`` / ``test_durable_session_service.py``. We
      keep one thin marker here documenting the retirement.
  (c) — the ``is_refresh_token_valid`` precedence bug is NOT fixed in this unit
      (out of scope: token_store); its frozen behavior REMAINS asserted here.

No real Neon: the persistence/session layer is faked in-memory.
"""

import os

import pytest

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

from app.api.v1.endpoints import _helpers  # noqa: E402
from app.auth import token_store  # noqa: E402

# --- (a)+(b) RETIRED: opaque 403 + contradictory docstring ------------------
# The restart -> opaque 403 behavior and the "re-create from stored credentials"
# docstring were the CURRENT failure this unit deliberately fixes (Step 10). The
# authoritative new-contract behavior (actionable 401, durable rehydration) is
# asserted in test_durable_session_api.py and test_durable_session_service.py.
# We retain this single marker test to document the traceable retirement: the
# helper no longer advertises a password-based re-creation it cannot perform.


def test_helper_no_longer_promises_password_recreation():
    """Traceable retirement of the comment<->behavior divergence (b).

    The old docstring claimed the helper re-created the session from stored
    credentials; the durable design removed cleartext credentials from memory,
    so that promise is gone. This asserts the divergence no longer exists."""
    doc = _helpers.get_user_futmondo_client.__doc__ or ""
    assert "stored credentials" not in doc


# --- (c) is_refresh_token_valid precedence bug (STILL FROZEN, not fixed) -----


class _Cursor:
    def __init__(self, row):
        self._row = row

    def execute(self, sql, params=None):
        return self

    def fetchone(self):
        return self._row


class _ConnCtx:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _FakeDB:
    db_type = "sqlite"

    def __init__(self, row):
        self._row = row
        self._cursor = _Cursor(row)

    def get_connection(self):
        return _ConnCtx()

    def get_cursor(self, conn):
        return self._cursor

    def adapt_params(self, sql):
        return sql


@pytest.fixture
def patch_token_db(monkeypatch):
    def _install(row):
        monkeypatch.setattr(token_store, "get_db", lambda: _FakeDB(row))

    return _install


def test_aware_future_token_wrongly_rejected(patch_token_db):
    """CHARACTERIZATION of the precedence BUG (do NOT fix here; out of scope).

    A timezone-aware, not-yet-expired token (the real Postgres/Turso shape) is
    wrongly rejected because the expiry expression's operator precedence
    evaluates to the datetime itself (truthy) and returns False."""
    from datetime import datetime, timedelta, timezone

    future_aware = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    patch_token_db((0, future_aware))  # revoked=0, aware future expiry
    assert token_store.is_refresh_token_valid("h") is False


def test_naive_future_token_accepted_today(patch_token_db):
    """The only shape accepted today: a NAIVE future timestamp."""
    from datetime import datetime, timedelta

    future_naive = (datetime.now() + timedelta(days=5)).isoformat()
    patch_token_db((0, future_naive))
    assert token_store.is_refresh_token_valid("h") is True
