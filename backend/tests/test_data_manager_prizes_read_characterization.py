"""Characterization safety net for the ``prizes`` read responsibility (rank 7).

Freezes the observable effect of ``get_prizes_by_team`` over the in-memory fake
(BR2.1/BR3.1): per-team aggregation across prize columns and the total, plus the
absent-team edge. Never ``assert True`` (BR2.2/BR2.3). No network/DB/credentials.
"""

import pytest

from app.services.data_manager_v2 import DataManagerV2


def _make_dm(fake_db):
    dm = DataManagerV2(skip_init=True)
    dm.db = fake_db
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS team_prizes (
                championship_id TEXT, team_id TEXT, ranking_prize INTEGER,
                mvp_prize INTEGER, points_prize INTEGER, dream_team_prize INTEGER
            )
            """
        )
    return dm


def test_get_prizes_by_team_sums_and_totals(fake_db):
    dm = _make_dm(fake_db)
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute(
            "INSERT INTO team_prizes VALUES (?, ?, ?, ?, ?, ?)", ("c1", "tA", 100, 50, 30, 20)
        )
        cursor.execute(
            "INSERT INTO team_prizes VALUES (?, ?, ?, ?, ?, ?)", ("c1", "tA", 10, 0, 5, 0)
        )
    prizes = dm.get_prizes_by_team("c1")
    assert prizes["tA"]["ranking"] == 110
    assert prizes["tA"]["mvp"] == 50
    assert prizes["tA"]["points"] == 35
    assert prizes["tA"]["dream_team"] == 20
    assert prizes["tA"]["total"] == 215


def test_get_prizes_by_team_absent_team_not_in_map(fake_db):
    dm = _make_dm(fake_db)
    assert dm.get_prizes_by_team("c1") == {}
