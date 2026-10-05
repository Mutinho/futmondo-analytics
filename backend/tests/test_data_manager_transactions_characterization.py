"""Characterization safety net for the ``transactions`` responsibility (rank 9).

Freezes the observable effect of the ``DataManagerV2`` transaction methods over
the in-memory fake (BR2.1/BR3.1): the legacy no-op writer, the pressroom batch
upsert (users/teams/players/transactions), per-player grouping, per-user
spent/received/profit aggregation, and raw payloads. Never ``assert True``
(BR2.2/BR2.3). No network/real DB/credentials.

The production SQLite path uses ``cursor.executemany``; the shared fake cursor
only implements ``execute``, so we decorate it exactly as the ``performance``
characterization test does.
"""

import pytest

from app.services.data_manager_v2 import DataManagerV2


class _ExecuteManyCursor:
    """Wrap a ``_FakeCursor`` adding ``executemany`` (SQLite batch path)."""

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
    _orig = fake_db.get_cursor
    fake_db.get_cursor = lambda conn: _ExecuteManyCursor(_orig(conn))
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
            "CREATE TABLE IF NOT EXISTS players (player_id TEXT PRIMARY KEY, name TEXT, role TEXT, real_team_id TEXT, real_team_name TEXT, slug TEXT, photo_url TEXT, last_updated TEXT)"
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                championship_id TEXT, api_transaction_id TEXT PRIMARY KEY, player_id TEXT,
                seller_user_id TEXT, buyer_user_id TEXT, seller_team_id TEXT, buyer_team_id TEXT,
                price INTEGER, transaction_date TEXT, matchday INTEGER, recorded_at TEXT
            )
            """
        )
    return dm


def _txn(tid, pid, buyer, seller, price):
    t = {"_id": tid, "_player": {"_id": pid, "name": pid}, "price": price, "created": ""}
    if buyer:
        t["_buyer"] = {"_id": buyer, "name": buyer}
    if seller:
        t["_seller"] = {"_id": seller, "name": seller}
    return t


def test_save_player_transactions_is_legacy_noop(fake_db):
    dm = _make_dm(fake_db)
    # Returns None and writes nothing (legacy hook).
    assert dm.save_player_transactions("p1", [{"owner": "x"}]) is None
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("SELECT COUNT(*) FROM transactions")
        assert cursor.fetchone()[0] == 0


def test_save_pressroom_transactions_upserts_entities_and_rows(fake_db):
    dm = _make_dm(fake_db)
    dm.save_pressroom_transactions("c1", [_txn("tx1", "p1", "buyerA", "sellerB", 1000)])
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("SELECT COUNT(*) FROM transactions")
        assert cursor.fetchone()[0] == 1
        cursor.execute(
            "SELECT player_id, buyer_user_id, seller_user_id, price FROM transactions WHERE api_transaction_id = ?",
            ("tx1",),
        )
        assert cursor.fetchone() == ("p1", "buyerA", "sellerB", 1000)
        cursor.execute("SELECT COUNT(*) FROM players WHERE player_id = ?", ("p1",))
        assert cursor.fetchone()[0] == 1


def test_save_pressroom_transactions_empty_is_noop(fake_db):
    dm = _make_dm(fake_db)
    dm.save_pressroom_transactions("c1", [])
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("SELECT COUNT(*) FROM transactions")
        assert cursor.fetchone()[0] == 0


def test_get_all_player_transactions_groups_by_player(fake_db):
    dm = _make_dm(fake_db)
    # Seed rows directly with NULL transaction_date so the production
    # ``row[2].isoformat() if row[2] else None`` branch yields None (the fake
    # stores datetimes as ISO strings, which .isoformat() cannot consume — that
    # raising path is exercised in production only with real driver datetimes).
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        for tid, price, buyer in (("tx1", 1000, "buyerA"), ("tx2", 2000, "buyerC")):
            cursor.execute(
                """
                INSERT INTO transactions
                (championship_id, api_transaction_id, player_id, seller_user_id,
                 buyer_user_id, seller_team_id, buyer_team_id, price,
                 transaction_date, matchday, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                ("c1", tid, "p1", "sellerB", buyer, "sellerB", buyer, price, None, 1, None),
            )
    grouped = dm.get_all_player_transactions("c1")
    assert set(grouped.keys()) == {"p1"}
    assert len(grouped["p1"]) == 2
    assert all(t["transaction_date"] is None for t in grouped["p1"])
    prices = sorted(t["price"] for t in grouped["p1"])
    assert prices == [1000, 2000]


def test_get_user_transactions_aggregates_spent_received_profit(fake_db):
    dm = _make_dm(fake_db)
    # buyerA buys p1 from sellerB for 1000; sellerB receives 1000.
    dm.save_pressroom_transactions("c1", [_txn("tx1", "p1", "buyerA", "sellerB", 1000)])
    stats = dm.get_user_transactions("c1")
    assert stats["buyerA"]["total_spent"] == 1000
    assert stats["buyerA"]["transaction_profit"] == -1000
    assert stats["sellerB"]["total_received"] == 1000
    assert stats["sellerB"]["transaction_profit"] == 1000


def test_get_transactions_raw_returns_rows(fake_db):
    dm = _make_dm(fake_db)
    dm.save_pressroom_transactions("c1", [_txn("tx1", "p1", "buyerA", "sellerB", 1000)])
    raw = dm.get_transactions_raw("c1")
    assert len(raw) == 1
    assert raw[0]["transaction_id"] == "tx1"
    assert raw[0]["player_id"] == "p1"
    assert raw[0]["price"] == 1000


def test_get_transactions_raw_unknown_championship_empty(fake_db):
    dm = _make_dm(fake_db)
    assert dm.get_transactions_raw("nope") == []
