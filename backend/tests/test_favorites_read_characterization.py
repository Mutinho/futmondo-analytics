"""Characterization tests (Step 3, BR6.1 / NFR4) — freeze the CURRENT shape.

These assert the observable response SHAPE of ``favorites/my`` and
``market/today`` produced by the code BEFORE the read-from-sync refactor:
exact contract keys, the ``position_order`` asc + ``value`` desc ordering of
favorites, the defaults applied when a numeric field is absent, and the
``market/today`` ``user_info`` block with
``available_for_bids = max_bid - active_bids_total``.

They run against the CURRENT favorites.py / market.py (live-route handlers),
doubling the Futmondo client (no network) and backing persistence with the
in-memory ``fake_db`` from conftest. No real DB, no credentials (gitleaks scans
tests).

Characterization-first: these MUST pass against the unchanged handlers so a
later data-source swap can be proven contract-preserving (BR6.1).
"""

import asyncio
import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import app.api.v1.endpoints.favorites as favorites_mod  # noqa: E402
import app.api.v1.endpoints.market as market_mod  # noqa: E402

CHAMPIONSHIP_ID = "champ-1"
USER_ID = "user-1"
TEAM_ID = "team-1"

# Current contract keys for favorites/my players[] (frozen BEFORE the refactor).
FAVORITE_KEYS = {
    "player_id", "name", "slug", "position", "position2", "team", "team_logo",
    "value", "change", "points", "average", "home_average", "away_average",
    "matches", "rating", "sofascore_rating", "sofascore_url", "starter_pct",
    "status", "position_order",
}


class _FakeRequest:
    """Minimal Request double exposing ``state.user`` as the endpoints read it."""

    def __init__(self, user_id=USER_ID):
        self.state = type("S", (), {})()
        self.state.user = {"user_id": user_id}


class _FakeFavoritesClient:
    """Doubles the live Futmondo client for favorites/my (no network)."""

    def __init__(self, players, user_id=USER_ID, team_id=TEAM_ID):
        self.user_id = user_id
        self._players = players
        self._team_id = team_id

    def get_championship_players(self, championship_id):
        return {"players": self._players}

    def get_matchday_standings(self, championship_id):
        return {"teams": [{"userid": self.user_id, "teamid": self._team_id}]}

    def get_userteam_roster(self, championship_id, team_id):
        return []


def _seed_favorites(db, fav_ids):
    with db.get_connection() as conn:
        cur = db.get_cursor(conn)
        cur.execute(
            "CREATE TABLE player_favorites (championship_id TEXT, user_id TEXT, player_id TEXT)"
        )
        for pid in fav_ids:
            cur.execute(
                "INSERT INTO player_favorites VALUES (?, ?, ?)",
                (CHAMPIONSHIP_ID, USER_ID, pid),
            )
        # Empty sofascore_cache so lookups return {} (frozen default behavior).
        cur.execute(
            "CREATE TABLE sofascore_cache (player_name TEXT, rating REAL, sofascore_url TEXT,"
            " matches_started INTEGER, season TEXT, matches_started_prev INTEGER, team TEXT)"
        )
        cur.execute(
            "CREATE TABLE team_standings (championship_id TEXT, team_id TEXT, matchday INTEGER, team_value INTEGER)"
        )
        # Synced tables present but EMPTY → read_favorites reports a sync-miss and
        # the handler falls back to the live route (the behavior frozen here).
        cur.execute(
            "CREATE TABLE players (player_id TEXT, name TEXT, role TEXT, role2 TEXT,"
            " slug TEXT, real_team_name TEXT, value INTEGER, points INTEGER, change INTEGER,"
            " home_average REAL, away_average REAL, matches INTEGER, status TEXT, real_team_id TEXT)"
        )
        cur.execute(
            "CREATE TABLE player_championship_stats (championship_id TEXT, player_id TEXT,"
            " owner_team_id TEXT, average_overall REAL)"
        )
        cur.execute(
            "CREATE TABLE player_performance (championship_id TEXT, player_id TEXT, points INTEGER)"
        )
        cur.execute(
            "CREATE TABLE market_today (championship_id TEXT, market_date TEXT, player_id TEXT,"
            " player_name TEXT, slug TEXT, position TEXT, position2 TEXT, team TEXT,"
            " team_logo TEXT, value INTEGER, change INTEGER, average REAL, home_average REAL,"
            " away_average REAL, matches_played INTEGER, points INTEGER)"
        )


def test_favorites_my_shape_order_and_defaults(fake_db, monkeypatch):
    """Freeze: exact keys, position_order+value ordering, numeric defaults."""
    _seed_favorites(fake_db, ["p-gk", "p-fw", "p-mf"])

    # Three free-agent favorites across positions; one carries no average dict
    # (freezes the default fallback change=0, averages None, matches=0, etc.).
    live_players = [
        {"id": "p-fw", "name": "Striker", "slug": "striker", "role": "delantero",
         "role2": "", "team": "Team A", "logo": "logoA", "value": 5000000,
         "change": 10, "points": 7, "average": {"average": 6.5, "homeAverage": 6.0,
         "awayAverage": 7.0, "matches": 8}, "rating": 0, "status": ""},
        {"id": "p-gk", "name": "Keeper", "slug": "keeper", "role": "portero",
         "role2": "", "team": "Team B", "logo": "logoB", "value": 3000000},
        {"id": "p-mf", "name": "Mid", "slug": "mid", "role": "centrocampista",
         "role2": "", "team": "Team C", "logo": "logoC", "value": 9000000,
         "average": {"average": 5.0, "matches": 3}},
    ]
    client = _FakeFavoritesClient(live_players)
    monkeypatch.setattr(favorites_mod, "get_user_futmondo_client", lambda req: client)
    monkeypatch.setattr(favorites_mod, "get_db", lambda: fake_db)

    resp = asyncio.run(favorites_mod.get_my_favorites(_FakeRequest(), CHAMPIONSHIP_ID))

    assert resp["success"] is True
    assert resp["total"] == 3
    players = resp["players"]
    # Order: position_order asc (portero 0, centrocampista 2, delantero 3),
    # then value desc within tie (none tie here).
    assert [p["player_id"] for p in players] == ["p-gk", "p-mf", "p-fw"]
    # Exact contract keys on every player.
    for p in players:
        assert set(p.keys()) == FAVORITE_KEYS
    # Defaults frozen for the keeper (no average dict supplied).
    gk = players[0]
    assert gk["change"] == 0
    assert gk["average"] == 0
    assert gk["home_average"] is None
    assert gk["away_average"] is None
    assert gk["matches"] == 0
    assert gk["rating"] == 0
    assert gk["status"] == ""
    assert gk["position_order"] == 0
    # sofascore defaults (empty cache → None).
    assert gk["sofascore_rating"] is None
    assert gk["sofascore_url"] is None
    assert gk["starter_pct"] is None


def test_favorites_my_empty_when_no_favorites(fake_db, monkeypatch):
    """Freeze: no favorites → {success, players:[], total:0}, no live call needed."""
    _seed_favorites(fake_db, [])
    client = _FakeFavoritesClient([])
    monkeypatch.setattr(favorites_mod, "get_user_futmondo_client", lambda req: client)
    monkeypatch.setattr(favorites_mod, "get_db", lambda: fake_db)

    resp = asyncio.run(favorites_mod.get_my_favorites(_FakeRequest(), CHAMPIONSHIP_ID))
    assert resp == {"success": True, "players": [], "total": 0}


# ---------------------------------------------------------------------------
# market/today — freeze user_info shape and available_for_bids derivation.
# ---------------------------------------------------------------------------


class _FakeMarketClient:
    def __init__(self, user_id=USER_ID, team_id=TEAM_ID, bid_players=None):
        self.user_id = user_id
        self.token = "fake-token-not-real"  # noqa: S105 (test double, not a secret)
        self.base_url = "https://example.invalid"
        self._team_id = team_id
        self._bid_players = bid_players or []
        self.session = self._Session(self._bid_players)

    def get_matchday_standings(self, championship_id):
        return {"teams": [{"userid": self.user_id, "teamid": self._team_id}]}

    class _Session:
        def __init__(self, bid_players):
            self._bid_players = bid_players

        def post(self, url, json=None, timeout=None):
            # Live bids call: return this user's bids.
            return _FakeResp(200, {"answer": self._bid_players})


class _FakeResp:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


def _seed_market(fake_db, market_rows, team_value=10000000):
    today = __import__("datetime").date.today().isoformat()
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        cur.execute(
            "CREATE TABLE user_championships (user_id TEXT, championship_id TEXT,"
            " futmondo_team_id TEXT, initial_budget INTEGER, excluded_teams TEXT, has_clauses INTEGER)"
        )
        cur.execute(
            "INSERT INTO user_championships VALUES (?, ?, ?, ?, ?, ?)",
            (USER_ID, CHAMPIONSHIP_ID, TEAM_ID, 200000000, None, 0),
        )
        cur.execute(
            "CREATE TABLE market_today (championship_id TEXT, market_date TEXT, raw_json TEXT)"
        )
        import json as _json
        for row in market_rows:
            cur.execute(
                "INSERT INTO market_today VALUES (?, ?, ?)",
                (CHAMPIONSHIP_ID, today, _json.dumps(row)),
            )
        cur.execute(
            "CREATE TABLE transactions (championship_id TEXT, seller_team_id TEXT, buyer_team_id TEXT,"
            " price INTEGER, market_value_at_purchase INTEGER, transaction_date TEXT)"
        )
        cur.execute(
            "CREATE TABLE team_standings (championship_id TEXT, team_id TEXT, matchday INTEGER, team_value INTEGER)"
        )
        cur.execute(
            "INSERT INTO team_standings VALUES (?, ?, ?, ?)",
            (CHAMPIONSHIP_ID, TEAM_ID, 1, team_value),
        )
        cur.execute(
            "CREATE TABLE team_prizes (championship_id TEXT, team_id TEXT, ranking_prize INTEGER,"
            " mvp_prize INTEGER, points_prize INTEGER, dream_team_prize INTEGER)"
        )
        cur.execute(
            "CREATE TABLE sofascore_cache (player_name TEXT, sofascore_id TEXT, rating REAL,"
            " goals INTEGER, assists INTEGER, appearances INTEGER, sofascore_url TEXT,"
            " matches_started INTEGER, season TEXT, matches_started_prev INTEGER)"
        )
        cur.execute(
            "CREATE TABLE player_favorites (championship_id TEXT, user_id TEXT, player_id TEXT)"
        )


def test_market_today_user_info_available_for_bids(fake_db, monkeypatch):
    """Freeze: user_info keys + available_for_bids = max_bid - active_bids_total."""
    market_rows = [
        {"id": "m1", "name": "Comp One", "slug": "comp-one", "team": "T", "logo": "",
         "role": "delantero", "role2": "", "value": 4000000, "price": 4000000,
         "change": 0, "average": {"average": 5.0, "matches": 2}, "points": 3,
         "computer": True, "photo": "", "expirationDate": ""},
    ]
    _seed_market(fake_db, market_rows, team_value=10000000)
    # Live bids: this user bids 1,000,000 on m1.
    bid_players = [{"id": "m1", "bid": {"price": 1000000, "id": "bid-1"}}]
    client = _FakeMarketClient(bid_players=bid_players)
    monkeypatch.setattr(market_mod, "get_db", lambda: fake_db)
    monkeypatch.setattr(
        market_mod, "get_user_futmondo_client", lambda req, _c=client: _c, raising=False
    )
    # _build_market_response imports get_user_futmondo_client from _helpers lazily;
    # patch the source too.
    import app.api.v1.endpoints._helpers as helpers_mod
    monkeypatch.setattr(helpers_mod, "get_user_futmondo_client", lambda req, _c=client: _c)
    # get_championship_config resolves get_db from db_connection lazily; make it
    # resolve to the seeded fake too.
    import app.services.db_connection as db_mod
    monkeypatch.setattr(db_mod, "get_db", lambda: fake_db)

    resp = asyncio.run(market_mod.get_market_today(_FakeRequest(), CHAMPIONSHIP_ID))

    assert resp["success"] is True
    ui = resp["user_info"]
    assert set(ui.keys()) == {
        "balance", "team_value", "max_bid", "active_bids_total",
        "active_bids_count", "available_for_bids",
    }
    assert ui["active_bids_total"] == 1000000
    assert ui["active_bids_count"] == 1
    # available_for_bids is exactly max_bid - active_bids_total (BR5.1).
    assert ui["available_for_bids"] == ui["max_bid"] - ui["active_bids_total"]
    # Player contract carries current_bid / current_bid_id from the live bid.
    player = next(p for p in resp["players"] if p["player_id"] == "m1")
    assert player["current_bid"] == 1000000
    assert player["current_bid_id"] == "bid-1"
