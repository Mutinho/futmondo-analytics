"""Tests for the enriched ``sync_read.favorites_read`` (Step 10, test-after;
BR3.1/BR4.1/BR4.2/BR5.2).

Exercise the real parameterized SQL against the in-memory ``fake_db``. The
authoritative source for points/change/averages/matches/status/team is now the
synced ``players`` row (not ``market_today``/``player_performance``). Covered:

- a favorite with POPULATED players columns → real enriched values;
- a favorite with NULL players columns → the BR5.2 defaults (0/0/None/None/0/'');
- team/team_logo resolved via ``LALIGA_TEAMS`` by ``real_team_id``;
- worst case (no LALIGA_TEAMS entry and no real_team_name) → ''/'';
- the exact 20-key contract and the sort order (position_order asc, value desc);
- a CHARACTERIZATION test freezing that the OLD points source
  (SUM(player_performance)) was 0 for a free agent, documenting the intentional
  switch to players.points.

No network, no real DB, no credentials (gitleaks scans tests).
"""

import os
from datetime import date

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

from app.core.constants import LALIGA_TEAMS  # noqa: E402
from app.services.sync_read import favorites_read  # noqa: E402

CHAMP = "champ-1"
USER = "user-1"

# A real LaLiga id present in the static map (Real Madrid).
RM_ID = "504e581e4d8bec9a670000c6"

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
    # players now carries the enrichment columns (post-migration shape).
    cur.execute(
        "CREATE TABLE players ("
        " player_id TEXT, name TEXT, role TEXT, role2 TEXT, slug TEXT,"
        " real_team_name TEXT, value INTEGER, points INTEGER, change INTEGER,"
        " home_average REAL, away_average REAL, matches INTEGER, status TEXT,"
        " real_team_id TEXT)"
    )
    cur.execute(
        "CREATE TABLE player_championship_stats (championship_id TEXT, player_id TEXT,"
        " owner_team_id TEXT, average_overall REAL)"
    )
    cur.execute(
        "CREATE TABLE market_today (championship_id TEXT, market_date TEXT, player_id TEXT,"
        " player_name TEXT, slug TEXT, position TEXT, position2 TEXT, team TEXT,"
        " team_logo TEXT, value INTEGER, change INTEGER, average REAL, home_average REAL,"
        " away_average REAL, matches_played INTEGER, points INTEGER)"
    )
    cur.execute(
        "CREATE TABLE sofascore_cache (player_name TEXT, rating REAL, sofascore_url TEXT,"
        " matches_started INTEGER, season TEXT, matches_started_prev INTEGER, team TEXT)"
    )
    cur.execute(
        "CREATE TABLE team_standings (championship_id TEXT, team_id TEXT, matchday INTEGER, team_value INTEGER)"
    )


def _fav(cur, pid):
    cur.execute("INSERT INTO player_favorites VALUES (?, ?, ?)", (CHAMP, USER, pid))


def _player(cur, pid, name, role, role2="", slug="", real_team="", value=0,
            points=None, change=None, home_average=None, away_average=None,
            matches=None, status=None, real_team_id=None):
    cur.execute(
        "INSERT INTO players VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (pid, name, role, role2, slug, real_team, value, points, change,
         home_average, away_average, matches, status, real_team_id),
    )


def _stats(cur, pid, owner=None, average_overall=None):
    cur.execute(
        "INSERT INTO player_championship_stats VALUES (?, ?, ?, ?)",
        (CHAMP, pid, owner, average_overall),
    )


def test_favorite_with_populated_columns_serves_real_values(fake_db):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _schema(cur)
        _fav(cur, "p1")
        _player(cur, "p1", "Striker", "delantero", slug="striker", value=5000000,
                points=123, change=-40000, home_average=6.2, away_average=5.8,
                matches=12, status="ok", real_team_id=RM_ID)
        _stats(cur, "p1", owner=None, average_overall=6.5)

    players, has_synced = favorites_read.read_favorites(fake_db, CHAMP, USER)

    assert has_synced is True
    assert len(players) == 1
    p = players[0]
    assert set(p.keys()) == FAVORITE_KEYS
    assert len(p.keys()) == 20
    assert p["points"] == 123
    assert p["change"] == -40000
    assert p["home_average"] == 6.2
    assert p["away_average"] == 5.8
    assert p["matches"] == 12
    assert p["status"] == "ok"
    assert p["value"] == 5000000
    assert p["average"] == 6.5
    # Team resolved via LALIGA_TEAMS by real_team_id.
    assert p["team"] == LALIGA_TEAMS[RM_ID]["name"] == "Real Madrid"
    assert p["team_logo"] == LALIGA_TEAMS[RM_ID]["logo"]
    assert p["rating"] == 0  # flat


def test_favorite_with_null_columns_falls_back_to_defaults(fake_db):
    """BR5.2: before the first enriched sync the columns are NULL → defaults."""
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _schema(cur)
        _fav(cur, "p1")
        _player(cur, "p1", "Keeper", "portero", slug="keeper", value=3200000,
                points=None, change=None, home_average=None, away_average=None,
                matches=None, status=None, real_team_id=RM_ID)
        _stats(cur, "p1", owner=None, average_overall=6.3)

    players, _ = favorites_read.read_favorites(fake_db, CHAMP, USER)
    p = players[0]
    assert p["points"] == 0
    assert p["change"] == 0
    assert p["home_average"] is None
    assert p["away_average"] is None
    assert p["matches"] == 0
    assert p["status"] == ""
    # value/average still served from the always-synced columns.
    assert p["value"] == 3200000
    assert p["average"] == 6.3


def test_team_fallback_to_real_team_name_when_not_in_laliga_map(fake_db):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _schema(cur)
        _fav(cur, "p1")
        _player(cur, "p1", "Guy", "defensa", real_team="Some FC", value=100,
                real_team_id="not-a-laliga-id")
        _stats(cur, "p1", owner=None)

    players, _ = favorites_read.read_favorites(fake_db, CHAMP, USER)
    p = players[0]
    # Name falls back to real_team_name; logo only comes from LALIGA_TEAMS → ''.
    assert p["team"] == "Some FC"
    assert p["team_logo"] == ""


def test_team_worst_case_empty_when_no_map_and_no_name(fake_db):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _schema(cur)
        _fav(cur, "p1")
        _player(cur, "p1", "Nobody", "defensa", real_team="", value=50,
                real_team_id=None)
        _stats(cur, "p1", owner=None)

    players, _ = favorites_read.read_favorites(fake_db, CHAMP, USER)
    p = players[0]
    assert p["team"] == ""
    assert p["team_logo"] == ""


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
            _player(cur, pid, pid, role, value=val)
            _stats(cur, pid, owner=None)

    players, _ = favorites_read.read_favorites(fake_db, CHAMP, USER)
    assert [p["player_id"] for p in players] == ["gk", "mf", "fw-rich", "fw-cheap"]


def test_characterization_old_points_source_was_zero_for_free_agent(fake_db):
    """CHARACTERIZATION (BR5.1): document the intentional source switch.

    The OLD favorites_read derived points from SUM(player_performance.points);
    a free agent has no per-matchday performance rows under its own id, so that
    aggregate was 0. We freeze that fact (seeding player_performance with NO
    rows for the favorite), then prove the NEW read serves players.points
    instead — a real non-zero value — so the change is explicit, not silent."""
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        _schema(cur)
        # player_performance exists but holds NO rows for this free agent —
        # exactly the condition under which the old SUM was 0.
        cur.execute(
            "CREATE TABLE player_performance (championship_id TEXT, player_id TEXT, points INTEGER)"
        )
        _fav(cur, "free")
        _player(cur, "free", "Free Agent", "delantero", value=1000000,
                points=250, real_team_id=RM_ID)
        _stats(cur, "free", owner=None)

        # Freeze the OLD behavior: the SUM over player_performance is 0 here.
        cur.execute(
            "SELECT COALESCE(SUM(points), 0) FROM player_performance"
            " WHERE championship_id = ? AND player_id = ?",
            (CHAMP, "free"),
        )
        assert cur.fetchone()[0] == 0

    players, _ = favorites_read.read_favorites(fake_db, CHAMP, USER)
    # NEW behavior: points comes from players.points, not the (zero) aggregate.
    assert players[0]["points"] == 250
