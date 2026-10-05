"""Characterization safety net for the ``teams-standings`` responsibility (rank 10).

Freezes the observable effect of the standings methods over the in-memory fake
(BR2.1/BR3.1): standings written/upserted, team + user upsert, round-ranking
accumulation across matchdays, latest-matchday query, history windowing,
team-by-id lookup, and streak ordering. Never ``assert True`` (BR2.2/BR2.3).
No network/real DB/credentials.
"""

import pytest

from app.services.data_manager_v2 import DataManagerV2


def _make_dm(fake_db):
    dm = DataManagerV2(skip_init=True)
    dm.db = fake_db
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS championships (championship_id TEXT PRIMARY KEY, name TEXT, created_at TEXT)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, username TEXT, last_updated TEXT)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS teams (team_id TEXT PRIMARY KEY, user_id TEXT, team_name TEXT, initial_budget INTEGER, last_updated TEXT)"
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS team_standings (
                championship_id TEXT, team_id TEXT, matchday INTEGER, position INTEGER,
                points INTEGER, points_this_matchday INTEGER, team_value INTEGER, recorded_at TEXT,
                PRIMARY KEY (championship_id, team_id, matchday)
            )
            """
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS player_performance (championship_id TEXT, player_id TEXT, matchday INTEGER, points INTEGER)"
        )
    return dm


def test_save_team_standing_writes_row(fake_db):
    dm = _make_dm(fake_db)
    # Production drives save_team_standing within an open transaction (the
    # standalone branch opens AND closes a connection; the shared in-memory fake
    # models a single connection, so we exercise the same-transaction path that
    # save_round_ranking uses in production — the asserted write effect is the same).
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        dm.save_team_standing(
            "c1",
            "tA",
            1,
            2,
            50,
            points_this_matchday=50,
            team_value=1000,
            conn=conn,
            cursor=cursor,
        )
        conn.commit()
    hist = dm.get_team_standings_history("c1")
    assert len(hist) == 1
    assert hist[0] == {
        "team_id": "tA",
        "matchday": 1,
        "position": 2,
        "points": 50,
        "points_this_matchday": 50,
        "team_value": 1000,
    }


def test_save_team_upserts_team_and_user(fake_db):
    dm = _make_dm(fake_db)
    dm.save_team("tA", "Team A", user_id="u1", owner_name="Alice")
    team = dm.get_team_by_id("tA")
    assert team == {"team_id": "tA", "user_id": "u1", "team_name": "Team A"}
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("SELECT username FROM users WHERE user_id = ?", ("u1",))
        assert cursor.fetchone()[0] == "Alice"


def test_save_round_ranking_accumulates_points(fake_db):
    dm = _make_dm(fake_db)
    dm.save_round_ranking(1, "c1", [{"id": "tA", "position": 1, "roundPoints": 40}])
    dm.save_round_ranking(2, "c1", [{"id": "tA", "position": 1, "roundPoints": 30}])
    assert dm.get_latest_matchday("c1") == 2
    hist = {h["matchday"]: h for h in dm.get_team_standings_history("c1")}
    assert hist[1]["points"] == 40
    assert hist[2]["points"] == 70  # accumulated 40 + 30
    assert hist[2]["points_this_matchday"] == 30


def test_get_latest_matchday_none_when_empty(fake_db):
    dm = _make_dm(fake_db)
    assert dm.get_latest_matchday("c1") is None


def test_get_team_standings_history_window(fake_db):
    dm = _make_dm(fake_db)
    for md in (1, 2, 3):
        dm.save_round_ranking(md, "c1", [{"id": "tA", "position": 1, "roundPoints": 10}])
    windowed = dm.get_team_standings_history("c1", window=2)
    assert sorted(h["matchday"] for h in windowed) == [2, 3]


def test_get_team_by_id_none_for_missing(fake_db):
    dm = _make_dm(fake_db)
    assert dm.get_team_by_id("ghost") is None
    assert dm.get_team_by_id("") is None


def test_get_player_streak_data_ordered(fake_db):
    dm = _make_dm(fake_db)
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        for md, pts in ((2, 20), (1, 10), (3, 30)):
            cursor.execute(
                "INSERT INTO player_performance VALUES (?, ?, ?, ?)", ("c1", "p1", md, pts)
            )
    streak = dm.get_player_streak_data("c1")
    assert [s["matchday"] for s in streak] == [1, 2, 3]
    assert [s["points"] for s in streak] == [10, 20, 30]


def test_get_player_streak_data_min_matchday_filter(fake_db):
    dm = _make_dm(fake_db)
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        for md in (1, 2, 3):
            cursor.execute(
                "INSERT INTO player_performance VALUES (?, ?, ?, ?)", ("c1", "p1", md, md)
            )
    streak = dm.get_player_streak_data("c1", min_matchday=2)
    assert [s["matchday"] for s in streak] == [2, 3]
