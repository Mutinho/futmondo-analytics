"""Characterization safety net for the ``users-stats-evolution`` responsibility (rank 12).

Freezes the observable effect of the user/stats/evolution methods over the
in-memory fake (BR2.1/BR3.1): name→user/team resolution with auto-create, the
moved ``_ensure_user`` / ``_get_or_create_user_id`` helpers, unique-player stats
aggregation (clauses + transactions), current points, evolution series, and
user-by-id. Never ``assert True`` (BR2.2/BR2.3). No network/real DB/credentials.

``get_users_unique_players_stats`` calls ``self.db.adapt_sql`` (a DDL rewrite that
is a passthrough on SQLite), which the shared fake does not implement; we attach
a passthrough ``adapt_sql`` to the fake for this suite only.
"""

import pytest

from app.services.data_manager_v2 import DataManagerV2


def _make_dm(fake_db):
    dm = DataManagerV2(skip_init=True)
    fake_db.adapt_sql = lambda sql: sql  # SQLite passthrough (no AUTOINCREMENT in these SELECTs)
    dm.db = fake_db
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
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
                points INTEGER, points_this_matchday INTEGER, team_value INTEGER, recorded_at TEXT
            )
            """
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS team_rosters (championship_id TEXT, team_id TEXT, player_id TEXT, matchday INTEGER)"
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clauses (
                championship_id TEXT, payer_team_id TEXT, payer_user_id TEXT,
                receiver_team_id TEXT, receiver_user_id TEXT, amount INTEGER
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                championship_id TEXT, buyer_team_id TEXT, seller_team_id TEXT, price INTEGER
            )
            """
        )
    return dm


def test_ensure_user_and_get_user_by_id(fake_db):
    dm = _make_dm(fake_db)
    dm._ensure_user("u1", "Alice")
    assert dm.get_user_by_id("u1") == {"user_id": "u1", "username": "Alice"}


def test_get_user_by_id_none_for_missing(fake_db):
    dm = _make_dm(fake_db)
    assert dm.get_user_by_id("ghost") is None
    assert dm.get_user_by_id("") is None


def test_get_or_create_user_id_creates_and_reuses(fake_db):
    dm = _make_dm(fake_db)
    uid1 = dm._get_or_create_user_id("Bob", "Bob")
    assert dm.get_user_by_id(uid1)["username"] == "Bob"
    # Second call by same username returns the same id (no duplicate).
    uid2 = dm._get_or_create_user_id("Bob", "Bob")
    assert uid1 == uid2


def test_get_user_id_by_name_resolves_existing_team(fake_db):
    dm = _make_dm(fake_db)
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", ("u1", "Alice"))
        cursor.execute(
            "INSERT INTO teams (team_id, user_id, team_name) VALUES (?, ?, ?)",
            ("t1", "u1", "Alice FC"),
        )
    info = dm.get_user_id_by_name("Alice")
    assert info == {"user_id": "u1", "team_id": "t1"}


def test_get_user_id_by_name_creates_when_absent(fake_db):
    dm = _make_dm(fake_db)
    info = dm.get_user_id_by_name("Newcomer")
    assert info is not None
    assert info["user_id"] and info["team_id"]
    # The created user is now resolvable.
    assert dm.get_user_by_id(info["user_id"])["username"] == "Newcomer"


def test_get_user_id_by_name_empty_returns_none(fake_db):
    dm = _make_dm(fake_db)
    assert dm.get_user_id_by_name("") is None


def test_get_all_users_with_points_latest_matchday(fake_db):
    dm = _make_dm(fake_db)
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", ("u1", "Alice"))
        cursor.execute(
            "INSERT INTO teams (team_id, user_id, team_name) VALUES (?, ?, ?)",
            ("t1", "u1", "Alice FC"),
        )
        cursor.execute(
            "INSERT INTO team_standings (championship_id, team_id, matchday, position, points) VALUES (?, ?, ?, ?, ?)",
            ("c1", "t1", 1, 1, 40),
        )
        cursor.execute(
            "INSERT INTO team_standings (championship_id, team_id, matchday, position, points) VALUES (?, ?, ?, ?, ?)",
            ("c1", "t1", 2, 1, 70),
        )
    rows = dm.get_all_users_with_points("c1")
    assert len(rows) == 1
    assert rows[0]["team_id"] == "t1"
    assert rows[0]["total_points"] == 70  # latest matchday


def test_get_evolution_data_from_db_series(fake_db):
    dm = _make_dm(fake_db)
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute(
            "INSERT INTO teams (team_id, user_id, team_name) VALUES (?, ?, ?)",
            ("t1", "u1", "Alice FC"),
        )
        cursor.execute(
            "INSERT INTO team_standings (championship_id, team_id, matchday, position, points) VALUES (?, ?, ?, ?, ?)",
            ("c1", "t1", 1, 1, 40),
        )
        cursor.execute(
            "INSERT INTO team_standings (championship_id, team_id, matchday, position, points) VALUES (?, ?, ?, ?, ?)",
            ("c1", "t1", 2, 2, 70),
        )
    evo = dm.get_evolution_data_from_db("c1")
    assert evo["matchdays"] == [1, 2]
    assert evo["teams"][0]["points_evolution"] == [40, 70]
    assert evo["teams"][0]["positions_evolution"] == [1, 2]


def test_get_users_unique_players_stats_aggregates(fake_db):
    dm = _make_dm(fake_db)
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", ("u1", "Alice"))
        cursor.execute(
            "INSERT INTO teams (team_id, user_id, team_name) VALUES (?, ?, ?)",
            ("t1", "u1", "Alice FC"),
        )
        cursor.execute(
            "INSERT INTO team_rosters (championship_id, team_id, player_id, matchday) VALUES (?, ?, ?, ?)",
            ("c1", "t1", "p1", 1),
        )
        cursor.execute(
            "INSERT INTO team_rosters (championship_id, team_id, player_id, matchday) VALUES (?, ?, ?, ?)",
            ("c1", "t1", "p2", 1),
        )
        cursor.execute(
            "INSERT INTO transactions (championship_id, buyer_team_id, seller_team_id, price) VALUES (?, ?, ?, ?)",
            ("c1", "t1", None, 500),
        )
    stats = dm.get_users_unique_players_stats("c1")
    by_team = {s["team_id"]: s for s in stats}
    assert by_team["t1"]["unique_players_count"] == 2
    assert by_team["t1"]["total_spent"] == 500
    assert by_team["t1"]["transaction_profit"] == -500
