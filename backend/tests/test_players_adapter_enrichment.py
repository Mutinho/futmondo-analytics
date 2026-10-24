"""Tests for the ``PlayersAdapter.save_players_batch`` enrichment (Step 6,
test-after; BR2.1).

Exercise the real parameterized SQLite batch path against the in-memory
``fake_db`` from conftest: the six enrichment columns
(``points``/``change``/``home_average``/``away_average``/``matches``/``status``)
are persisted on insert and overwritten on an upsert conflict
(``INSERT OR REPLACE`` by ``player_id``). No network, no real DB, no credentials.
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

from app.services.data_manager.players.infrastructure.players_adapter import (  # noqa: E402
    PlayersAdapter,
)


class _ExecuteManyCursor:
    """Decorate the shared fake cursor with ``executemany`` (SQLite batch path),
    exactly as the existing players/transactions characterization tests do."""

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


def _schema(cur):
    # players with the enriched shape (post-migration).
    cur.execute(
        "CREATE TABLE players ("
        " player_id TEXT PRIMARY KEY, name TEXT, role TEXT, role2 TEXT,"
        " real_team_id TEXT, real_team_name TEXT, slug TEXT, photo_url TEXT,"
        " value INTEGER, points INTEGER DEFAULT 0, change INTEGER DEFAULT 0,"
        " home_average REAL, away_average REAL, matches INTEGER DEFAULT 0,"
        " status TEXT DEFAULT '', last_updated TEXT)"
    )


def _adapter(fake_db):
    _orig = fake_db.get_cursor
    fake_db.get_cursor = lambda conn: _ExecuteManyCursor(_orig(conn))
    adapter = PlayersAdapter.__new__(PlayersAdapter)
    adapter.dm = type("DM", (), {"db": fake_db})()
    return adapter


def _read(fake_db, pid):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        cur.execute(
            "SELECT points, change, home_average, away_average, matches, status, value"
            " FROM players WHERE player_id = ?",
            (pid,),
        )
        return cur.fetchone()


def test_batch_persists_enrichment_columns(fake_db):
    with fake_db.get_connection() as conn:
        _schema(fake_db.get_cursor(conn))
    adapter = _adapter(fake_db)

    count = adapter.save_players_batch(
        [
            {
                "id": "p1",
                "name": "Striker",
                "role": "delantero",
                "value": 5000000,
                "points": 123,
                "change": -40000,
                "home_average": 6.2,
                "away_average": 5.8,
                "matches": 12,
                "status": "ok",
            }
        ]
    )
    assert count == 1
    points, change, home, away, matches, status, value = _read(fake_db, "p1")
    assert points == 123
    assert change == -40000
    assert home == 6.2
    assert away == 5.8
    assert matches == 12
    assert status == "ok"
    assert value == 5000000


def test_batch_updates_enrichment_columns_on_conflict(fake_db):
    with fake_db.get_connection() as conn:
        _schema(fake_db.get_cursor(conn))
    adapter = _adapter(fake_db)

    adapter.save_players_batch(
        [{"id": "p1", "name": "Old", "points": 1, "change": 2, "matches": 3, "status": "injured",
          "home_average": 1.0, "away_average": 2.0}]
    )
    # Second sync with new values for the same player → overwrite.
    adapter.save_players_batch(
        [{"id": "p1", "name": "New", "points": 99, "change": -5, "matches": 20, "status": "ok",
          "home_average": 7.1, "away_average": 6.4}]
    )

    points, change, home, away, matches, status, _ = _read(fake_db, "p1")
    assert (points, change, home, away, matches, status) == (99, -5, 7.1, 6.4, 20, "ok")


def test_batch_applies_defaults_for_missing_enrichment(fake_db):
    with fake_db.get_connection() as conn:
        _schema(fake_db.get_cursor(conn))
    adapter = _adapter(fake_db)

    # Only identity fields; enrichment missing → 0/''/None defaults applied.
    adapter.save_players_batch([{"id": "p1", "name": "Bare"}])
    points, change, home, away, matches, status, _ = _read(fake_db, "p1")
    assert points == 0
    assert change == 0
    assert home is None
    assert away is None
    assert matches == 0
    assert status == ""
