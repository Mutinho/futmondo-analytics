"""Characterization safety net for the ``performance`` responsibility (rank 3).

Freezes the observable effect of ``save_player_performance`` /
``save_player_performance_batch`` / ``get_player_performance_history`` over the
in-memory SQLite fake (BR2.1/BR3.1): rows written, the batch return count, the
single-record delegation, player/window filters, and the empty-batch edge.
Never ``assert True`` (BR2.2/BR2.3). No network/real DB/credentials.
"""

from app.services.data_manager_v2 import DataManagerV2


class _ExecuteManyCursor:
    """Wrap a ``_FakeCursor`` adding ``executemany`` (the production SQLite path
    uses ``cursor.executemany`` for the batch insert; the shared fake cursor
    only implements ``execute``). This keeps the real parameterized SQL running
    against the in-memory DB so the test asserts the true rows-written effect.
    """

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


def _make_dm(fake_db):
    dm = DataManagerV2(skip_init=True)
    # Decorate the fake's cursor factory with executemany (SQLite batch path).
    _orig_get_cursor = fake_db.get_cursor
    fake_db.get_cursor = lambda conn: _ExecuteManyCursor(_orig_get_cursor(conn))
    dm.db = fake_db
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS championships "
            "(championship_id TEXT PRIMARY KEY, name TEXT, created_at TEXT)"
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS player_performance (
                championship_id TEXT, player_id TEXT, team_id TEXT, matchday INTEGER,
                points INTEGER, value INTEGER, was_best_player BOOLEAN, recorded_at TEXT,
                PRIMARY KEY (championship_id, player_id, team_id, matchday)
            )
            """
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS team_standings "
            "(championship_id TEXT, team_id TEXT, matchday INTEGER)"
        )
    return dm


def test_save_batch_returns_count_and_writes_rows(fake_db):
    dm = _make_dm(fake_db)
    n = dm.save_player_performance_batch(
        "champ1",
        [
            {"player_id": "p1", "team_id": "t1", "matchday": 1, "points": 10},
            {"player_id": "p2", "team_id": "t1", "matchday": 1, "points": 5, "value": 20},
        ],
    )
    assert n == 2
    rows = dm.get_player_performance_history("champ1")
    assert len(rows) == 2
    by_id = {r["player_id"]: r for r in rows}
    assert by_id["p1"]["points"] == 10
    assert by_id["p2"]["value"] == 20


def test_save_batch_empty_returns_zero(fake_db):
    dm = _make_dm(fake_db)
    assert dm.save_player_performance_batch("champ1", []) == 0


def test_save_single_delegates_to_batch(fake_db):
    dm = _make_dm(fake_db)
    dm.save_player_performance(
        "champ1", "p9", "t1", 3, 7, value=None, was_best_player=True
    )
    rows = dm.get_player_performance_history("champ1")
    assert len(rows) == 1
    assert rows[0]["player_id"] == "p9"
    assert rows[0]["was_best_player"] is True


def test_history_filters_by_player_ids(fake_db):
    dm = _make_dm(fake_db)
    dm.save_player_performance_batch(
        "champ1",
        [
            {"player_id": "p1", "team_id": "t1", "matchday": 1, "points": 1},
            {"player_id": "p2", "team_id": "t1", "matchday": 1, "points": 2},
        ],
    )
    rows = dm.get_player_performance_history("champ1", player_ids=["p2"])
    assert [r["player_id"] for r in rows] == ["p2"]


def test_history_empty_when_no_rows(fake_db):
    dm = _make_dm(fake_db)
    assert dm.get_player_performance_history("champ1") == []
