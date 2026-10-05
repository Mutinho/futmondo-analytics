"""Characterization safety net for the ``punishments-bonuses`` responsibility (rank 5).

Freezes the observable effect of ``save_punishments_bonuses`` /
``get_user_punishments_bonuses`` over the in-memory fake so behavior is identical
before/after the DDD extraction (BR2.1/BR3.1). Asserts the effect — rows written,
net adjustment, type filtering, skip edges — never ``assert True`` (BR2.2/BR2.3).
No network, no real DB, no credentials (BR2.3/NFR6).
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
            "CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, username TEXT UNIQUE)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS teams (team_id TEXT PRIMARY KEY, user_id TEXT, team_name TEXT)"
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS punishments_bonuses (
                championship_id TEXT, news_id TEXT PRIMARY KEY, user_id TEXT, team_id TEXT,
                user_name TEXT, type TEXT, amount INTEGER, admin_name TEXT, created_date TEXT
            )
            """
        )
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", ("u1", "Alice"))
        cursor.execute(
            "INSERT INTO teams (team_id, user_id, team_name) VALUES (?, ?, ?)",
            ("t1", "u1", "Alice"),
        )
    return dm


def _item(news_id, styp, qty):
    return {
        "_id": news_id,
        "styp": styp,
        "data": {"quantity": qty, "to": "Alice", "admin": "Boss"},
        "created": "",
    }


def test_save_and_aggregate_bonus_and_punishment(fake_db):
    dm = _make_dm(fake_db)
    dm.save_punishments_bonuses("champ1", [_item("n1", "bonus", 500), _item("n2", "punish", 200)])
    stats = dm.get_user_punishments_bonuses("champ1")
    assert stats["t1"]["total_bonuses"] == 500
    assert stats["t1"]["total_punishments"] == 200
    assert stats["t1"]["net_adjustment"] == 300
    assert stats["t1"]["bonus_count"] == 1
    assert stats["t1"]["punishment_count"] == 1


def test_save_skips_non_punish_bonus_types(fake_db):
    dm = _make_dm(fake_db)
    dm.save_punishments_bonuses("champ1", [_item("n1", "news", 500)])
    assert dm.get_user_punishments_bonuses("champ1") == {}


def test_save_skips_zero_quantity(fake_db):
    dm = _make_dm(fake_db)
    dm.save_punishments_bonuses("champ1", [_item("n1", "bonus", 0)])
    assert dm.get_user_punishments_bonuses("champ1") == {}


def test_save_empty_list_is_noop(fake_db):
    dm = _make_dm(fake_db)
    dm.save_punishments_bonuses("champ1", [])
    assert dm.get_user_punishments_bonuses("champ1") == {}


def test_aggregate_unknown_championship_empty(fake_db):
    dm = _make_dm(fake_db)
    assert dm.get_user_punishments_bonuses("nope") == {}
