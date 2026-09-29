"""Characterization tests for the assistant usage tracker (BR4.1-BR4.3).

These freeze the CURRENT observable behavior of ``AssistantUsageTracker`` BEFORE
the persistence is moved behind ``AssistantUsagePort`` into the infrastructure
adapter. After extraction the same assertions must hold against the port +
adapter pair.

The tracker owns the ``assistant_usage`` table. Its observable contract:

BR4.1 — quota is checked BEFORE serving: ``can_make_request()`` returns
         ``(True, "")`` when under budget and ``(False, <reason>)`` when the
         monthly token limit or the daily request limit is reached.
BR4.2 — consumption is recorded AFTER serving: ``record_usage()`` accumulates
         token/request counters that a later ``can_make_request`` /
         ``get_usage_summary`` observes.
BR4.3 — ``_ensure_table`` runs ``CREATE TABLE IF NOT EXISTS`` idempotently:
         constructing the tracker twice against the same DB does not error.

The DB boundary is injected by pointing the module-level ``get_db`` at the
in-memory ``fake_db`` fixture (SQLite ``:memory:``). This substitutes the DB at
its seam; it does NOT monkeypatch any SQL text.
"""

import app.services.assistant.facade as facade_mod
from app.services.assistant_service import (
    DAILY_REQUEST_LIMIT,
    MONTHLY_TOKEN_LIMIT,
    AssistantUsageTracker,
)


def _tracker_on(fake_db, monkeypatch):
    """Build a tracker whose DB boundary is the in-memory fake."""
    monkeypatch.setattr(facade_mod, "get_db", lambda: fake_db)
    return AssistantUsageTracker()


# --- BR4.3: CREATE TABLE IF NOT EXISTS is idempotent -------------------------


def test_ensure_table_is_idempotent(fake_db, monkeypatch):
    """Constructing the tracker twice against the same DB does not error (BR4.3)."""
    _tracker_on(fake_db, monkeypatch)
    # Second construction re-runs CREATE TABLE IF NOT EXISTS on the same DB.
    AssistantUsageTracker()
    # The table exists and is queryable.
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        cur.execute("SELECT COUNT(*) FROM assistant_usage")
        assert cur.fetchone()[0] == 0


# --- BR4.1: quota checked before serving -------------------------------------


def test_can_make_request_allows_when_under_budget(fake_db, monkeypatch):
    """A fresh tracker is under budget and permits the request (BR4.1)."""
    tracker = _tracker_on(fake_db, monkeypatch)
    allowed, reason = tracker.can_make_request()
    assert allowed is True
    assert reason == ""


def test_can_make_request_blocks_when_monthly_token_limit_reached(fake_db, monkeypatch):
    """Reaching the monthly token limit blocks the request with a reason (BR4.1)."""
    tracker = _tracker_on(fake_db, monkeypatch)
    # Record usage that reaches the monthly token ceiling.
    tracker.record_usage(MONTHLY_TOKEN_LIMIT, 0)
    allowed, reason = tracker.can_make_request()
    assert allowed is False
    assert "límite mensual" in reason
    # No credential/token material leaks into the user-facing reason.
    assert "password" not in reason.lower()


def test_can_make_request_blocks_when_daily_request_limit_reached(fake_db, monkeypatch):
    """Reaching the daily request limit blocks the request with a reason (BR4.1)."""
    from datetime import date, datetime

    tracker = _tracker_on(fake_db, monkeypatch)
    today = date.today().isoformat()
    # Seed the daily row (keyed by the ISO date) at the request limit.
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        cur.execute(
            fake_db.adapt_params(
                "INSERT INTO assistant_usage (month, total_input_tokens, "
                "total_output_tokens, total_requests, updated_at) "
                "VALUES (?, 0, 0, ?, ?)"
            ),
            (today, DAILY_REQUEST_LIMIT, datetime.now().isoformat()),
        )
    allowed, reason = tracker.can_make_request()
    assert allowed is False
    assert "límite diario" in reason


# --- BR4.2: consumption recorded after serving -------------------------------


def test_record_usage_accumulates_monthly_tokens(fake_db, monkeypatch):
    """record_usage accumulates token/request counters observable later (BR4.2)."""
    tracker = _tracker_on(fake_db, monkeypatch)
    tracker.record_usage(100, 50)
    tracker.record_usage(200, 25)
    summary = tracker.get_usage_summary()
    # 100+50 + 200+25 = 375 tokens accumulated for the current month.
    assert summary["tokens_used"] == 375
    assert summary["monthly_requests"] == 2
    assert summary["tokens_limit"] == MONTHLY_TOKEN_LIMIT
    assert summary["requests_daily_limit"] == DAILY_REQUEST_LIMIT
