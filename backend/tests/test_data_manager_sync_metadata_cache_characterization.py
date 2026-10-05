"""Characterization safety net for the ``sync-metadata-cache`` responsibility (rank 13).

Freezes the observable effect of ``get_last_sync_metadata`` /
``update_sync_metadata`` / ``should_update_cache`` over the in-memory fake
(BR2.1/BR3.1): upsert then read-back, not-found None, and the always-true cache
predicate. Never ``assert True`` for the SQL methods (BR2.2/BR2.3). No network/DB/creds.
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
            """
            CREATE TABLE IF NOT EXISTS sync_metadata (
                championship_id TEXT, data_type TEXT, last_sync_id TEXT, last_sync_date TEXT,
                last_sync_matchday INTEGER, records_synced INTEGER, sync_duration_seconds REAL,
                sync_status TEXT, error_message TEXT, updated_at TEXT,
                PRIMARY KEY (championship_id, data_type)
            )
            """
        )
    return dm


def test_update_then_get_roundtrips_metadata(fake_db):
    dm = _make_dm(fake_db)
    dm.update_sync_metadata(
        "c1", "transactions", last_sync_id="tx99", last_sync_matchday=5, records_synced=42
    )
    meta = dm.get_last_sync_metadata("c1", "transactions")
    assert meta is not None
    assert meta["last_sync_id"] == "tx99"
    assert meta["last_sync_matchday"] == 5
    assert meta["records_synced"] == 42
    assert meta["sync_status"] == "success"


def test_get_last_sync_metadata_not_found_returns_none(fake_db):
    dm = _make_dm(fake_db)
    assert dm.get_last_sync_metadata("c1", "unknown") is None


def test_update_sync_metadata_upserts_in_place(fake_db):
    dm = _make_dm(fake_db)
    dm.update_sync_metadata("c1", "clauses", last_sync_id="a", records_synced=1)
    dm.update_sync_metadata("c1", "clauses", last_sync_id="b", records_synced=2)
    meta = dm.get_last_sync_metadata("c1", "clauses")
    assert meta["last_sync_id"] == "b"
    assert meta["records_synced"] == 2
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute(
            "SELECT COUNT(*) FROM sync_metadata WHERE championship_id = ? AND data_type = ?",
            ("c1", "clauses"),
        )
        assert cursor.fetchone()[0] == 1  # upsert, not duplicate


def test_should_update_cache_always_true(fake_db):
    dm = _make_dm(fake_db)
    assert dm.should_update_cache("transactions") is True
    assert dm.should_update_cache("anything") is True
