"""Unit tests for ``sync_read.favorites_read`` (Step 5, test-after).

Exercise the real parameterized SQL against the in-memory ``fake_db`` from
conftest. No network, no real DB, no credentials (gitleaks scans tests).

Covers (BR2.1/BR2.2/BR3.1/BR6.1):
- free-agent favorites mapped to the exact contract keys;
- ordering preserved (position_order asc, value desc);
- 0 synced rows → ``has_synced=False`` fallback signal;
- ``market_today`` lookup supplies change/averages/matches/points/value;
- defaults applied when a favorite is NOT in today's ``market_today``;
- non-favorites and owned (non-free-agent) players excluded;
- empty favorites → ``([], True)`` (correct empty, not a sync-miss).
"""

import os
from datetime import date

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

from app.services.sync_read import favorites_read  # noqa: E402

CHAMP = "champ-1"
USER = "user-1"

FAVORITE_KEYS = {
    "player_id", "name", "slug", "position", "position2", "team", "team_logo",
    "value", "change", "points", "average", "home_average", "away_average",
    "matches", "rating", "sofascore_rating", "sofascore_url", "starter_pct",
    "status", "position_order",
}


def _schema(cur):
    cur.execute(
        "CREATE TABLE player_favorites (championship_id TEXT, user_id TEXT, player_id TEXT)"
    )
    cur.execute(
        "CREATE TABLE players (player_id TEXT, name TEXT, role TEXT, role2 TEXT,"
        " slug TEXT, real_team_name TEXT, value INTEGER)"
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
    # sofascore_cache must exist for build_sofascore_map; empty here.
    cur.execute(
        "CREATE TABLE sofascore_cache (player_name TEXT, rating REAL, sofascore_url TEXT,"
        " matches_started INTEGER, season TEXT, matches_started_prev INTEGER, team TEXT)"
    )
    cur.execute(
        "CREATE TABLE team_standings (championship_id TEXT, team_id TEXT, matchday INTEGER, team_value INTEGER)"
    )


def _fav(cur, pid):
    cur.execute("INSERT INTO player_favorites VALUES (?, ?, ?)", (CHAMP, USER, pid))


def _player(cur, pid, name, role, role2="", slug="", real_team="", value=0):
    cur.execute(
        "INSERT INTO players VALUES (?, ?, ?, ?, ?, ?, ?)",
        (pid, name, role, role2, slug, real_team, value),
    )


def _stats(cur, pid, owner=None, average_overall=None):
    cur.execute(
        "INSERT INTO player_championship_stats VALUES (?, ?, ?, ?)",
        (CHAMP, pid, owner, average_overall),
    )


def _perf(cur, pid, points):
    cur.execute(
        "INSERT INTO player_performance VALUES (?, ?, ?)", (CHAMP, pid, points)
    )


def _market(cur, pid, name, **kw):
    today = date.today().isoformat()
    cur.execute(
        "INSERT INTO market_today VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            CHAMP, today, pid, name,
            kw.get("slug", ""), kw.get("position", ""), kw.get("position2", ""),
            kw.get("team", ""), kw.get("team_logo", ""), kw.get("value", 0),
            kw.get("change", 0), kw.get("average"), kw.get("home_average"),
            kw.get("away_average"), kw.get("matches_played", 0), kw.get("points", 0),
        ),
    )


def test_free_agent_favorites_mapped_with_contract_keys_and_market_stats(fake_db):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _schema(cur)
        _fav(cur, "p1")
        _player(cur, "p1", "Striker", "delantero", slug="striker")
        _stats(cur, "p1", owner=None)  # free agent
        _market(cur, "p1", "Striker", value=5000000, change=10, average=6.5,
                home_average=6.0, away_average=7.0, matches_played=8, points=7,
                team="Team A", team_logo="logoA", slug="striker", position2="")

    players, has_synced = favorites_read.read_favorites(fake_db, CHAMP, USER)

    assert has_synced is True
    assert len(players) == 1
    p = players[0]
    assert set(p.keys()) == FAVORITE_KEYS
    assert p["player_id"] == "p1"
    assert p["value"] == 5000000
    assert p["change"] == 10
    assert p["average"] == 6.5
    assert p["home_average"] == 6.0
    assert p["away_average"] == 7.0
    assert p["matches"] == 8
    assert p["points"] == 7
    assert p["team"] == "Team A"
    assert p["team_logo"] == "logoA"
    assert p["position"] == "delantero"
    assert p["position_order"] == 3
    # No sofascore cache row → defaults.
    assert p["sofascore_rating"] is None
    assert p["sofascore_url"] is None
    assert p["starter_pct"] is None
    # Flat rating / status frozen defaults.
    assert p["rating"] == 0
    assert p["status"] == ""


def test_order_preserved_position_asc_then_value_desc(fake_db):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _schema(cur)
        for pid, role, val in [
            ("fw-cheap", "delantero", 2000000),
            ("gk", "portero", 1000000),
            ("fw-rich", "delantero", 9000000),
            ("mf", "centrocampista", 5000000),
        ]:
            _fav(cur, pid)
            _player(cur, pid, pid, role)
            _stats(cur, pid, owner=None)
            _market(cur, pid, pid, value=val)

    players, has_synced = favorites_read.read_favorites(fake_db, CHAMP, USER)
    assert has_synced is True
    # portero(0), centrocampista(2), delantero(3) — within delantero, value desc.
    assert [p["player_id"] for p in players] == ["gk", "mf", "fw-rich", "fw-cheap"]


def test_zero_synced_rows_signals_fallback(fake_db):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _schema(cur)
        _fav(cur, "p1")  # favorite exists but no synced player/stats row for it

    players, has_synced = favorites_read.read_favorites(fake_db, CHAMP, USER)
    assert players == []
    assert has_synced is False


def test_synced_fields_served_when_favorite_absent_from_market_today(fake_db):
    """REGRESSION: a favorite NOT in today's market_today still shows value,
    average and points from the always-synced tables (players,
    player_championship_stats, player_performance) — not zeros."""
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _schema(cur)
        _fav(cur, "p1")
        _player(cur, "p1", "Keeper", "portero", role2="", slug="keeper",
                real_team="Team B", value=3200000)
        _stats(cur, "p1", owner=None, average_overall=6.3)
        _perf(cur, "p1", 12)
        _perf(cur, "p1", 8)  # aggregates to 20
        # No market_today row for p1.

    players, has_synced = favorites_read.read_favorites(fake_db, CHAMP, USER)
    assert has_synced is True
    p = players[0]
    # value / average / points come from the synced tables (the fix).
    assert p["value"] == 3200000
    assert p["average"] == 6.3
    assert p["points"] == 20
    # change / home / away / matches only live in market_today → defaults.
    assert p["change"] == 0
    assert p["home_average"] is None
    assert p["away_average"] is None
    assert p["matches"] == 0
    # team / slug fall back to players.*
    assert p["team"] == "Team B"
    assert p["slug"] == "keeper"


def test_excludes_non_favorites_and_owned_players(fake_db):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _schema(cur)
        # Favorite + free agent → included.
        _fav(cur, "free")
        _player(cur, "free", "Free Agent", "defensa")
        _stats(cur, "free", owner=None)
        _market(cur, "free", "Free Agent", value=4000000)
        # Favorite BUT owned (owner set) → excluded.
        _fav(cur, "owned")
        _player(cur, "owned", "Owned Guy", "defensa")
        _stats(cur, "owned", owner="team-x")
        _market(cur, "owned", "Owned Guy", value=8000000)
        # NOT a favorite, free agent → excluded.
        _player(cur, "other", "Other", "defensa")
        _stats(cur, "other", owner=None)
        _market(cur, "other", "Other", value=9000000)

    players, has_synced = favorites_read.read_favorites(fake_db, CHAMP, USER)
    assert has_synced is True
    assert [p["player_id"] for p in players] == ["free"]


def test_empty_favorites_returns_empty_not_fallback(fake_db):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _schema(cur)
        # No favorites seeded.

    players, has_synced = favorites_read.read_favorites(fake_db, CHAMP, USER)
    assert players == []
    # Correct empty answer, NOT a sync-miss (no live fallback needed).
    assert has_synced is True
