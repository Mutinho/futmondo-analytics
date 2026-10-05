"""Characterization safety net for the ``match-odds`` responsibility (rank 1).

Freezes the observable effect of ``DataManagerV2.save_match_odds`` /
``get_match_odds`` over the in-memory SQLite fake (``fake_db``) so the behavior
is identical before and after the DDD extraction (BR2.1/BR3.1). Asserts the
effect — rows written, payload shape, matchday/upcoming filters, and the
empty-result edge — never ``assert True`` and never a mirror spec (BR2.2/BR2.3).

No network, no real DB, no credentials (BR2.3/NFR6): everything runs on the
shared ``:memory:`` SQLite fake seeded from literals.
"""

from datetime import datetime, timedelta

import pytest

from app.services.data_manager_v2 import DataManagerV2


def _make_dm(fake_db):
    """Build a facade bound to the in-memory fake, with the odds schema seeded."""
    dm = DataManagerV2(skip_init=True)
    dm.db = fake_db
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS championships (
                championship_id TEXT PRIMARY KEY,
                name TEXT,
                created_at TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS match_odds (
                championship_id TEXT,
                match_id TEXT,
                round_id TEXT,
                matchday INTEGER,
                match_date TEXT,
                home_team_id TEXT,
                home_team_name TEXT,
                away_team_id TEXT,
                away_team_name TEXT,
                odds_home REAL,
                odds_draw REAL,
                odds_away REAL,
                best_bookmaker_home TEXT,
                best_bookmaker_draw TEXT,
                best_bookmaker_away TEXT,
                fetched_at TEXT,
                PRIMARY KEY (championship_id, match_id)
            )
            """
        )
    return dm


def _match(match_id, matchday, date_iso):
    return {
        "id": match_id,
        "matchday": matchday,
        "date": date_iso,
        "roundId": "r1",
        "homeTeam": {"id": "home1", "name": "Home FC"},
        "awayTeam": {"id": "away1", "name": "Away FC"},
        "odds": {
            "sels": [
                {"sn": "Home FC", "ssn": "1", "odds": [{"c": 1.5, "bid": "bookieH"}]},
                {"sn": "draw", "odds": [{"c": 3.2, "bid": "bookieD"}]},
                {"sn": "Away FC", "odds": [{"c": 6.0, "bid": "bookieA"}]},
            ]
        },
    }


def test_save_match_odds_writes_rows_and_parses_best_prices(fake_db):
    dm = _make_dm(fake_db)
    dm.save_match_odds("champ1", [_match("m1", 10, "2099-01-01T20:00:00Z")], matchday=10)

    rows = dm.get_match_odds("champ1")
    assert len(rows) == 1
    row = rows[0]
    assert row["match_id"] == "m1"
    assert row["matchday"] == 10
    assert row["home_team_name"] == "Home FC"
    assert row["away_team_name"] == "Away FC"
    assert row["odds_home"] == 1.5
    assert row["odds_draw"] == 3.2
    assert row["odds_away"] == 6.0
    assert row["best_bookmaker_home"] == "bookieH"
    assert row["best_bookmaker_draw"] == "bookieD"
    assert row["best_bookmaker_away"] == "bookieA"


def test_save_match_odds_empty_list_is_noop(fake_db):
    dm = _make_dm(fake_db)
    dm.save_match_odds("champ1", [])
    assert dm.get_match_odds("champ1") == []


def test_save_match_odds_skips_matches_without_id(fake_db):
    dm = _make_dm(fake_db)
    dm.save_match_odds("champ1", [{"matchday": 5, "odds": {}}], matchday=5)
    assert dm.get_match_odds("champ1") == []


def test_get_match_odds_filters_by_matchday(fake_db):
    dm = _make_dm(fake_db)
    dm.save_match_odds("champ1", [_match("m1", 10, "2099-01-01T20:00:00Z")], matchday=10)
    dm.save_match_odds("champ1", [_match("m2", 11, "2099-02-01T20:00:00Z")], matchday=11)

    rows = dm.get_match_odds("champ1", matchday=11)
    assert [r["match_id"] for r in rows] == ["m2"]


def test_get_match_odds_upcoming_only_excludes_past_matches(fake_db):
    dm = _make_dm(fake_db)
    past = (datetime.now() - timedelta(days=10)).isoformat()
    future = (datetime.now() + timedelta(days=10)).isoformat()
    dm.save_match_odds("champ1", [_match("past", 1, past)], matchday=1)
    dm.save_match_odds("champ1", [_match("future", 2, future)], matchday=2)

    upcoming = dm.get_match_odds("champ1", upcoming_only=True)
    assert "future" in [r["match_id"] for r in upcoming]
    assert "past" not in [r["match_id"] for r in upcoming]


def test_get_match_odds_unknown_championship_returns_empty(fake_db):
    dm = _make_dm(fake_db)
    assert dm.get_match_odds("does-not-exist") == []
