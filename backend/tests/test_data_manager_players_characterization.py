"""Characterization safety net for the ``players`` responsibility (rank 11).

Freezes the observable effect of the ``DataManagerV2`` player methods over the
in-memory fake (BR2.1/BR3.1): single/batch/photo upserts, player-by-id lookup,
championship-stats batch, points aggregation, and — critically — the
``delete_orphan_players`` ``DELETE ... NOT IN`` set-replacement effect, frozen
VERBATIM (BR3.3, OQ2 deferred): orphans absent from the live list AND from every
history table are deleted; players with history are kept; an empty live list is
a safety no-op. Never ``assert True`` (BR2.2/BR2.3). No network/real DB/credentials.

The batch paths use ``cursor.executemany``; the shared fake cursor is decorated
exactly as the ``performance``/``transactions`` characterization tests do.
"""

import pytest

from app.services.data_manager_v2 import DataManagerV2


class _ExecuteManyCursor:
    def __init__(self, fake_cursor):
        self._fc = fake_cursor

    def execute(self, sql, params=None):
        return self._fc.execute(sql, params)

    def executemany(self, sql, seq_of_params):
        for params in seq_of_params:
            self._fc.execute(sql, params)
        return None

    def fetchone(self):
        return self._fc.fetchone()

    def fetchall(self):
        return self._fc.fetchall()

    @property
    def rowcount(self):
        return self._fc.rowcount


def _make_dm(fake_db, with_points_schema=False):
    dm = DataManagerV2(skip_init=True)
    _orig = fake_db.get_cursor
    fake_db.get_cursor = lambda conn: _ExecuteManyCursor(_orig(conn))
    dm.db = fake_db
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS championships (championship_id TEXT PRIMARY KEY, name TEXT, created_at TEXT)"
        )
        if with_points_schema:
            # get_all_players_with_points queries p.id / p.team columns.
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS players (id TEXT PRIMARY KEY, name TEXT, role TEXT, team TEXT)"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS player_performance (championship_id TEXT, player_id TEXT, points INTEGER)"
            )
        else:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS players (player_id TEXT PRIMARY KEY, name TEXT, role TEXT, role2 TEXT, real_team_id TEXT, real_team_name TEXT, slug TEXT, photo_url TEXT, value INTEGER, last_updated TEXT)"
            )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS player_championship_stats (championship_id TEXT, player_id TEXT, owner_team_id TEXT, owner_team_name TEXT, owner_user_id TEXT, clause_price INTEGER, suggested_clause INTEGER, average_last_five REAL, average_overall REAL, clause_date TEXT, updated_at TEXT, PRIMARY KEY (championship_id, player_id))"
        )
        for t in ("transactions", "player_performance", "team_rosters", "dream_teams_mvps"):
            if t == "player_performance" and with_points_schema:
                continue
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {t} (player_id TEXT)")
    return dm


def test_save_player_upserts_and_returns_id(fake_db):
    dm = _make_dm(fake_db)
    rid = dm.save_player({"id": "p1", "name": "Messi", "role": "FW"})
    assert rid == "p1"
    assert dm.get_player_by_id("p1")["name"] == "Messi"


def test_save_player_missing_id_returns_none(fake_db):
    dm = _make_dm(fake_db)
    assert dm.save_player({"name": "NoId"}) is None


def test_save_players_batch_counts_processed(fake_db):
    dm = _make_dm(fake_db)
    n = dm.save_players_batch(
        [{"id": "p1", "name": "A"}, {"id": "p2", "name": "B"}, {"name": "skip"}]
    )
    assert n == 2
    assert dm.get_player_by_id("p1") is not None
    assert dm.get_player_by_id("p2") is not None


def test_save_players_batch_empty_returns_zero(fake_db):
    dm = _make_dm(fake_db)
    assert dm.save_players_batch([]) == 0


def test_save_players_derives_photo_url(fake_db):
    dm = _make_dm(fake_db)
    dm.save_players([{"id": "p1", "name": "A", "photo": "abc.png"}])
    row = dm.get_player_by_id("p1")
    assert row["photo_url"] == "https://static01.mondocore.com/futmondo/img/faces/64/abc.png"


def test_get_player_by_id_none_for_missing(fake_db):
    dm = _make_dm(fake_db)
    assert dm.get_player_by_id("ghost") is None
    assert dm.get_player_by_id("") is None


def test_save_player_championship_stats_batch(fake_db):
    dm = _make_dm(fake_db)
    dm.save_player_championship_stats(
        "c1",
        [
            {
                "player_id": "p1",
                "owner_team_id": "t1",
                "clause_price": "100",
                "average_overall": "7.5",
            },
        ],
    )
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute(
            "SELECT clause_price, average_overall, owner_team_name FROM player_championship_stats WHERE player_id = ?",
            ("p1",),
        )
        row = cursor.fetchone()
    assert row[0] == 100  # coerced to int
    assert row[1] == 7.5  # coerced to float
    assert row[2] == "t1"  # owner_team_name falls back to owner_team_id


def test_delete_orphan_players_removes_unreferenced_only(fake_db):
    dm = _make_dm(fake_db)
    # Three players: live1 (in API list), orphan (no refs), kept (has a transaction row).
    for pid in ("live1", "orphan", "kept"):
        dm.save_player({"id": pid, "name": pid})
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("INSERT INTO transactions (player_id) VALUES (?)", ("kept",))
    deleted = dm.delete_orphan_players(["live1"])
    assert deleted == 1  # only 'orphan' removed
    assert dm.get_player_by_id("live1") is not None  # in API list
    assert dm.get_player_by_id("kept") is not None  # has history
    assert dm.get_player_by_id("orphan") is None  # set-replaced out (DELETE ... NOT IN)


def test_delete_orphan_players_empty_live_list_is_safety_noop(fake_db):
    dm = _make_dm(fake_db)
    dm.save_player({"id": "p1", "name": "A"})
    assert dm.delete_orphan_players([]) == 0
    assert dm.get_player_by_id("p1") is not None  # never wiped when API returned nothing


def test_get_all_players_with_points_aggregates(fake_db):
    dm = _make_dm(fake_db, with_points_schema=True)
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute(
            "INSERT INTO players (id, name, role, team) VALUES (?, ?, ?, ?)",
            ("p1", "Messi", "FW", "Barca"),
        )
        cursor.execute(
            "INSERT INTO player_performance (championship_id, player_id, points) VALUES (?, ?, ?)",
            ("c1", "p1", 10),
        )
        cursor.execute(
            "INSERT INTO player_performance (championship_id, player_id, points) VALUES (?, ?, ?)",
            ("c1", "p1", 15),
        )
    rows = dm.get_all_players_with_points("c1")
    assert len(rows) == 1
    assert rows[0]["player_id"] == "p1"
    assert rows[0]["total_points"] == 25
