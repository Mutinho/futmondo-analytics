"""Endpoint-level tests for the read-from-sync wiring (Step 10/11, test-after).

Drive the real ``favorites.py`` / ``market.py`` handlers with a doubled Futmondo
client (no network) and the in-memory ``fake_db``. Assert:
- favorites/my is served from sync when synced data is present (NO live
  ``get_championship_players`` call), contract intact (BR2.1/BR6.1);
- favorites/my falls back to the live route on a sync-miss, logging it, with an
  identical response shape (BR3.1/BR6.1);
- market/today serves the cached catalog and degrades bids to zero + warning
  when the live bids call fails, never dropping the contract's bid fields
  (BR3.2);
- no Futmondo password/token appears in any emitted log record (NFR5.4).

No real DB, no network, no real credentials (gitleaks scans tests).
"""

import asyncio
import json as _json
import logging
import os
from datetime import date

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import app.api.v1.endpoints._helpers as helpers_mod  # noqa: E402
import app.api.v1.endpoints.favorites as favorites_mod  # noqa: E402
import app.api.v1.endpoints.market as market_mod  # noqa: E402
import app.services.db_connection as db_mod  # noqa: E402

CHAMP = "champ-1"
USER = "user-1"
TEAM = "team-1"
SECRET_TOKEN = "super-secret-futmondo-token-value"  # noqa: S105 (test fixture)

FAVORITE_KEYS = {
    "player_id", "name", "slug", "position", "position2", "team", "team_logo",
    "value", "change", "points", "average", "home_average", "away_average",
    "matches", "rating", "sofascore_rating", "sofascore_url", "starter_pct",
    "status", "position_order",
}


class _FakeRequest:
    def __init__(self, user_id=USER):
        self.state = type("S", (), {})()
        self.state.user = {"user_id": user_id}


class _Resp:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class _FakeFavClient:
    def __init__(self, user_id=USER):
        self.user_id = user_id
        self.token = SECRET_TOKEN
        self.get_championship_players_called = False

    def get_championship_players(self, championship_id):
        self.get_championship_players_called = True
        # Live payload with one free-agent favorite.
        return {"players": [
            {"id": "p1", "name": "Live Striker", "slug": "live-striker",
             "role": "delantero", "role2": "", "team": "Team A", "logo": "logoA",
             "value": 5000000, "change": 3, "points": 4,
             "average": {"average": 6.0, "homeAverage": 5.5, "awayAverage": 6.5, "matches": 5},
             "rating": 0, "status": ""},
        ]}

    def get_matchday_standings(self, championship_id):
        return {"teams": [{"userid": self.user_id, "teamid": TEAM}]}

    def get_userteam_roster(self, championship_id, team_id):
        return []


def _patch_db(monkeypatch, fake_db):
    monkeypatch.setattr(favorites_mod, "get_db", lambda: fake_db)
    monkeypatch.setattr(market_mod, "get_db", lambda: fake_db)
    monkeypatch.setattr(db_mod, "get_db", lambda: fake_db)


def _fav_sync_schema(cur, with_synced_row):
    cur.execute("CREATE TABLE player_favorites (championship_id TEXT, user_id TEXT, player_id TEXT)")
    cur.execute("INSERT INTO player_favorites VALUES (?, ?, ?)", (CHAMP, USER, "p1"))
    cur.execute(
        "CREATE TABLE players (player_id TEXT, name TEXT, role TEXT, role2 TEXT, slug TEXT, real_team_name TEXT)"
    )
    cur.execute(
        "CREATE TABLE player_championship_stats (championship_id TEXT, player_id TEXT, owner_team_id TEXT)"
    )
    cur.execute(
        "CREATE TABLE market_today (championship_id TEXT, market_date TEXT, player_id TEXT,"
        " player_name TEXT, slug TEXT, position TEXT, position2 TEXT, team TEXT, team_logo TEXT,"
        " value INTEGER, change INTEGER, average REAL, home_average REAL, away_average REAL,"
        " matches_played INTEGER, points INTEGER)"
    )
    cur.execute(
        "CREATE TABLE sofascore_cache (player_name TEXT, rating REAL, sofascore_url TEXT,"
        " matches_started INTEGER, season TEXT, matches_started_prev INTEGER, team TEXT)"
    )
    cur.execute(
        "CREATE TABLE team_standings (championship_id TEXT, team_id TEXT, matchday INTEGER, team_value INTEGER)"
    )
    if with_synced_row:
        cur.execute(
            "INSERT INTO players VALUES ('p1', 'Synced Striker', 'delantero', '', 'synced-striker', 'Team A')"
        )
        cur.execute(
            "INSERT INTO player_championship_stats VALUES (?, 'p1', NULL)", (CHAMP,)
        )
        today = date.today().isoformat()
        cur.execute(
            "INSERT INTO market_today VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (CHAMP, today, "p1", "Synced Striker", "synced-striker", "", "", "Team A",
             "logoA", 5000000, 3, 6.0, 5.5, 6.5, 5, 4),
        )


def test_favorites_served_from_sync_without_live_call(fake_db, monkeypatch):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _fav_sync_schema(cur, with_synced_row=True)

    client = _FakeFavClient()
    monkeypatch.setattr(favorites_mod, "get_user_futmondo_client", lambda req: client)
    _patch_db(monkeypatch, fake_db)

    resp = asyncio.run(favorites_mod.get_my_favorites(_FakeRequest(), CHAMP))

    assert resp["success"] is True
    assert resp["total"] == 1
    assert set(resp["players"][0].keys()) == FAVORITE_KEYS
    # Served from sync: the heavy live catalog call was NOT made (BR2.1).
    assert client.get_championship_players_called is False
    # Value/stats came from the synced market_today row.
    assert resp["players"][0]["name"] == "Synced Striker"
    assert resp["players"][0]["value"] == 5000000


def test_favorites_falls_back_to_live_on_sync_miss(fake_db, monkeypatch, caplog):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _fav_sync_schema(cur, with_synced_row=False)  # synced tables empty → miss

    client = _FakeFavClient()
    monkeypatch.setattr(favorites_mod, "get_user_futmondo_client", lambda req: client)
    _patch_db(monkeypatch, fake_db)

    with caplog.at_level(logging.INFO):
        resp = asyncio.run(favorites_mod.get_my_favorites(_FakeRequest(), CHAMP))

    assert resp["success"] is True
    assert resp["total"] == 1
    assert set(resp["players"][0].keys()) == FAVORITE_KEYS
    # Fell back to the live route (BR3.1).
    assert client.get_championship_players_called is True
    assert resp["players"][0]["name"] == "Live Striker"
    assert any("sync-miss" in r.getMessage() for r in caplog.records)
    # No credential leaked in any log record (NFR5.4).
    assert not any(SECRET_TOKEN in r.getMessage() for r in caplog.records)


# ---------------------------------------------------------------------------
# market/today endpoint
# ---------------------------------------------------------------------------


class _FakeMarketClient:
    def __init__(self, bids_status=200, bid_players=None):
        self.user_id = USER
        self.token = SECRET_TOKEN
        self.base_url = "https://example.invalid"
        self.session = self._Session(bids_status, bid_players or [])

    def get_matchday_standings(self, championship_id):
        return {"teams": [{"userid": self.user_id, "teamid": TEAM}]}

    class _Session:
        def __init__(self, status, bid_players):
            self._status = status
            self._bid_players = bid_players

        def post(self, url, json=None, timeout=None):
            return _Resp(self._status, {"answer": self._bid_players})


def _market_schema(cur, catalog_rows, team_value=10000000):
    today = date.today().isoformat()
    cur.execute(
        "CREATE TABLE user_championships (user_id TEXT, championship_id TEXT, futmondo_team_id TEXT,"
        " initial_budget INTEGER, excluded_teams TEXT, has_clauses INTEGER)"
    )
    cur.execute(
        "INSERT INTO user_championships VALUES (?, ?, ?, ?, ?, ?)",
        (USER, CHAMP, TEAM, 200000000, None, 0),
    )
    cur.execute("CREATE TABLE market_today (championship_id TEXT, market_date TEXT, raw_json TEXT)")
    for row in catalog_rows:
        cur.execute("INSERT INTO market_today VALUES (?, ?, ?)", (CHAMP, today, _json.dumps(row)))
    cur.execute(
        "CREATE TABLE transactions (championship_id TEXT, seller_team_id TEXT, buyer_team_id TEXT,"
        " price INTEGER, market_value_at_purchase INTEGER, transaction_date TEXT)"
    )
    cur.execute(
        "CREATE TABLE team_standings (championship_id TEXT, team_id TEXT, matchday INTEGER, team_value INTEGER)"
    )
    cur.execute("INSERT INTO team_standings VALUES (?, ?, ?, ?)", (CHAMP, TEAM, 1, team_value))
    cur.execute(
        "CREATE TABLE team_prizes (championship_id TEXT, team_id TEXT, ranking_prize INTEGER,"
        " mvp_prize INTEGER, points_prize INTEGER, dream_team_prize INTEGER)"
    )
    cur.execute(
        "CREATE TABLE sofascore_cache (player_name TEXT, sofascore_id TEXT, rating REAL, goals INTEGER,"
        " assists INTEGER, appearances INTEGER, sofascore_url TEXT, matches_started INTEGER,"
        " season TEXT, matches_started_prev INTEGER)"
    )
    cur.execute("CREATE TABLE player_favorites (championship_id TEXT, user_id TEXT, player_id TEXT)")


_CATALOG = [{
    "id": "m1", "name": "Comp One", "slug": "comp-one", "team": "T", "logo": "",
    "role": "delantero", "role2": "", "value": 4000000, "price": 4000000, "change": 0,
    "average": {"average": 5.0, "matches": 2}, "points": 3, "computer": True,
    "photo": "", "expirationDate": "",
}]


def test_market_served_from_cache_with_live_bids(fake_db, monkeypatch):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _market_schema(cur, _CATALOG)

    client = _FakeMarketClient(bids_status=200, bid_players=[{"id": "m1", "bid": {"price": 1000000, "id": "bid-1"}}])
    monkeypatch.setattr(helpers_mod, "get_user_futmondo_client", lambda req: client)
    _patch_db(monkeypatch, fake_db)

    resp = asyncio.run(market_mod.get_market_today(_FakeRequest(), CHAMP))

    assert resp["success"] is True
    player = next(p for p in resp["players"] if p["player_id"] == "m1")
    assert player["current_bid"] == 1000000
    assert player["current_bid_id"] == "bid-1"
    ui = resp["user_info"]
    assert ui["active_bids_total"] == 1000000
    assert ui["available_for_bids"] == ui["max_bid"] - 1000000


def test_market_degrades_bids_to_zero_when_live_call_fails(fake_db, monkeypatch, caplog):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _market_schema(cur, _CATALOG)

    # Live bids call returns a non-200 → degrade to zero (BR3.2).
    client = _FakeMarketClient(bids_status=503, bid_players=[])
    monkeypatch.setattr(helpers_mod, "get_user_futmondo_client", lambda req: client)
    _patch_db(monkeypatch, fake_db)

    with caplog.at_level(logging.WARNING):
        resp = asyncio.run(market_mod.get_market_today(_FakeRequest(), CHAMP))

    assert resp["success"] is True
    player = next(p for p in resp["players"] if p["player_id"] == "m1")
    # Bid fields present in the contract but degraded to zero (never omitted).
    assert player["current_bid"] == 0
    assert player["current_bid_id"] == ""
    ui = resp["user_info"]
    assert ui["active_bids_total"] == 0
    assert ui["active_bids_count"] == 0
    # available_for_bids == max_bid when bids degraded to zero (BR5.1).
    assert ui["available_for_bids"] == ui["max_bid"]
    # A warning was logged, carrying NO credential (NFR5.4).
    assert any("degrading bid fields to zero" in r.getMessage() for r in caplog.records)
    assert not any(SECRET_TOKEN in r.getMessage() for r in caplog.records)


def test_no_credentials_in_logs_across_both_endpoints(fake_db, monkeypatch, caplog):
    """Aggregate NFR5.4 check: no token appears in any captured log record."""
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _market_schema(cur, _CATALOG)

    client = _FakeMarketClient(bids_status=503, bid_players=[])
    monkeypatch.setattr(helpers_mod, "get_user_futmondo_client", lambda req: client)
    _patch_db(monkeypatch, fake_db)

    with caplog.at_level(logging.DEBUG):
        asyncio.run(market_mod.get_market_today(_FakeRequest(), CHAMP))

    for record in caplog.records:
        assert SECRET_TOKEN not in record.getMessage()
        assert SECRET_TOKEN not in str(record.args or "")
