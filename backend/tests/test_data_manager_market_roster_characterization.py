"""Characterization safety net for the ``market-roster`` responsibility (rank 8).

Freezes the observable effect of ``save_market_players`` / ``save_team_roster`` /
``get_free_agent_candidates`` over the in-memory fake (BR2.1/BR3.1): rows written,
team auto-creation, free-agent filtering. Never ``assert True`` (BR2.2/BR2.3).
No network/DB/credentials.
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
            "CREATE TABLE IF NOT EXISTS teams (team_id TEXT PRIMARY KEY, team_name TEXT, user_id TEXT)"
        )
        cursor.execute("CREATE TABLE IF NOT EXISTS players (player_id TEXT PRIMARY KEY, name TEXT)")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS player_market_data (
                championship_id TEXT, player_id TEXT, matchday INTEGER, market_price INTEGER,
                availability TEXT, market_statistics TEXT, recorded_at TEXT,
                PRIMARY KEY (championship_id, player_id, matchday)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS team_rosters (
                championship_id TEXT, team_id TEXT, player_id TEXT, matchday INTEGER,
                formation_position TEXT, is_starter INTEGER, lineup_order INTEGER, recorded_at TEXT,
                PRIMARY KEY (championship_id, team_id, player_id, matchday)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS player_championship_stats (
                championship_id TEXT, player_id TEXT, owner_team_id TEXT,
                clause_price INTEGER, suggested_clause INTEGER,
                average_last_five REAL, average_overall REAL
            )
            """
        )
    return dm


def test_save_market_players_writes_rows(fake_db):
    dm = _make_dm(fake_db)
    dm.save_market_players(
        "c1", [{"id": "p1", "marketPrice": 1000, "availability": "ok"}], matchday=3
    )
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute(
            "SELECT player_id, matchday, market_price, availability FROM player_market_data"
        )
        row = cursor.fetchone()
    assert row == ("p1", 3, 1000, "ok")


def test_save_market_players_skips_missing_id(fake_db):
    dm = _make_dm(fake_db)
    dm.save_market_players("c1", [{"marketPrice": 10}], matchday=1)
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("SELECT COUNT(*) FROM player_market_data")
        assert cursor.fetchone()[0] == 0


def test_save_team_roster_autocreates_team_and_writes_roster(fake_db):
    dm = _make_dm(fake_db)
    dm.save_team_roster(
        "c1", "teamX", [{"id": "p1", "position": "GK", "isStarter": True}], matchday=2
    )
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("SELECT team_id FROM teams WHERE team_id = ?", ("teamX",))
        assert cursor.fetchone() is not None
        cursor.execute(
            "SELECT player_id, formation_position FROM team_rosters WHERE team_id = ?", ("teamX",)
        )
        assert cursor.fetchone() == ("p1", "GK")


def test_get_free_agent_candidates_only_unowned(fake_db):
    dm = _make_dm(fake_db)
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute(
            "INSERT INTO players (player_id, name) VALUES (?, ?)", ("free", "Free Agent")
        )
        cursor.execute("INSERT INTO players (player_id, name) VALUES (?, ?)", ("owned", "Owned"))
        cursor.execute(
            "INSERT INTO player_championship_stats VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("c1", "free", None, 50, 60, 7.0, 6.5),
        )
        cursor.execute(
            "INSERT INTO player_championship_stats VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("c1", "owned", "teamA", 50, 60, 7.0, 6.5),
        )
    agents = dm.get_free_agent_candidates("c1")
    ids = [a["player_id"] for a in agents]
    assert ids == ["free"]
    assert agents[0]["name"] == "Free Agent"


def test_get_free_agent_candidates_empty(fake_db):
    dm = _make_dm(fake_db)
    assert dm.get_free_agent_candidates("c1") == []
