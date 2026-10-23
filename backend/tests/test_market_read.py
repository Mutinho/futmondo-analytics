"""Unit tests for ``sync_read.market_read`` (Step 7, test-after).

Covers (BR4.1/BR5.1/BR3.2):
- catalog read from the cache (``market_today.raw_json``);
- 0 rows → ``None`` fallback signal;
- the pure ``available_for_bids`` calc, including the degraded-to-zero bids path.

Uses the in-memory ``fake_db`` from conftest. No network, no real DB, no
credentials (gitleaks scans tests).
"""

import json as _json
import os
from datetime import date

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

from app.services.sync_read import market_read  # noqa: E402

CHAMP = "champ-1"


def _schema(cur):
    cur.execute(
        "CREATE TABLE market_today (championship_id TEXT, market_date TEXT, raw_json TEXT)"
    )


def _row(cur, player):
    cur.execute(
        "INSERT INTO market_today VALUES (?, ?, ?)",
        (CHAMP, date.today().isoformat(), _json.dumps(player)),
    )


def test_catalog_read_from_cache(fake_db):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _schema(cur)
        _row(cur, {"id": "m1", "name": "Comp One", "value": 4000000, "computer": True})
        _row(cur, {"id": "m2", "name": "Comp Two", "value": 2000000, "computer": True})

    players = market_read.read_market_catalog(fake_db, CHAMP)
    assert players is not None
    assert {p["id"] for p in players} == {"m1", "m2"}
    # Full dict shape preserved from raw_json (same as the live payload).
    m1 = next(p for p in players if p["id"] == "m1")
    assert m1["name"] == "Comp One"
    assert m1["value"] == 4000000
    assert m1["computer"] is True


def test_zero_rows_returns_none_fallback_signal(fake_db):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _schema(cur)
        # No rows for today.

    assert market_read.read_market_catalog(fake_db, CHAMP) is None


def test_available_for_bids_pure_calc():
    # Normal case: max_bid - active_bids_total.
    assert market_read.available_for_bids(10000000, 3000000) == 7000000


def test_available_for_bids_with_degraded_zero_bids():
    # Degraded path (BR3.2): when the live bids call fails, active_bids_total is
    # 0, so available_for_bids == max_bid exactly.
    max_bid = 8500000
    assert market_read.available_for_bids(max_bid, 0) == max_bid
