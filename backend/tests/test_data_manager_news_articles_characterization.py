"""Characterization safety net for the ``news-articles`` responsibility (rank 2).

Freezes the observable effect of ``DataManagerV2.save_matchday_article`` /
``get_matchday_article`` / ``save_pressroom_news`` /
``get_matchday_data_for_news`` over the in-memory SQLite fake, so the behavior
is identical before and after extraction (BR2.1/BR3.1). Asserts the effect —
rows written, payload shape, the ``return None`` not-found edge, the
``ValueError`` guard, and the no-op ``save_pressroom_news`` — never
``assert True`` (BR2.2/BR2.3). No network/real DB/credentials (BR2.3/NFR6).
"""

import pytest

from app.services.data_manager_v2 import DataManagerV2


def _make_dm(fake_db):
    dm = DataManagerV2(skip_init=True)
    dm.db = fake_db
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS championships "
            "(championship_id TEXT PRIMARY KEY, name TEXT, created_at TEXT)"
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS matchday_articles (
                championship_id TEXT,
                matchday INTEGER,
                article TEXT,
                summary_json TEXT,
                generated_at TEXT,
                updated_at TEXT,
                PRIMARY KEY (championship_id, matchday)
            )
            """
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS teams "
            "(team_id TEXT PRIMARY KEY, team_name TEXT, user_id TEXT)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, username TEXT)"
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS team_standings (
                championship_id TEXT, team_id TEXT, matchday INTEGER,
                position INTEGER, points INTEGER, points_this_matchday INTEGER
            )
            """
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS players (player_id TEXT PRIMARY KEY, name TEXT)"
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS player_performance (
                championship_id TEXT, player_id TEXT, team_id TEXT, matchday INTEGER,
                points INTEGER, was_best_player BOOLEAN
            )
            """
        )
    return dm


def test_save_and_get_matchday_article_roundtrip(fake_db):
    dm = _make_dm(fake_db)
    dm.save_matchday_article("champ1", 7, "La jornada fue épica", summary={"mvp": "p1"})

    stored = dm.get_matchday_article("champ1", 7)
    assert stored is not None
    assert stored["championship_id"] == "champ1"
    assert stored["matchday"] == 7
    assert stored["article"] == "La jornada fue épica"
    assert stored["summary"] == {"mvp": "p1"}


def test_save_matchday_article_without_summary_stores_none(fake_db):
    dm = _make_dm(fake_db)
    dm.save_matchday_article("champ1", 3, "Sin resumen")
    stored = dm.get_matchday_article("champ1", 3)
    assert stored["summary"] is None


def test_save_matchday_article_requires_mandatory_fields(fake_db):
    dm = _make_dm(fake_db)
    with pytest.raises(ValueError):
        dm.save_matchday_article("champ1", None, "x")


def test_get_matchday_article_not_found_returns_none(fake_db):
    dm = _make_dm(fake_db)
    assert dm.get_matchday_article("champ1", 99) is None


def test_save_pressroom_news_is_noop(fake_db):
    dm = _make_dm(fake_db)
    # The optimized schema intentionally skips pressroom news (legacy behavior).
    assert dm.save_pressroom_news("champ1", [{"_id": "n1"}, {"_id": "n2"}]) is None


def test_get_matchday_data_for_news_builds_payload(fake_db):
    dm = _make_dm(fake_db)
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        cur.execute("INSERT INTO teams VALUES ('t1', 'Team One', 'u1')")
        cur.execute("INSERT INTO users VALUES ('u1', 'User One')")
        cur.execute(
            "INSERT INTO team_standings VALUES ('champ1', 't1', 5, 1, 100, 20)"
        )
        cur.execute(
            "INSERT INTO team_standings VALUES ('champ1', 't1', 4, 2, 80, 15)"
        )
        cur.execute("INSERT INTO players VALUES ('p1', 'Player One')")
        cur.execute(
            "INSERT INTO player_performance VALUES ('champ1', 'p1', 't1', 5, 12, 1)"
        )

    data = dm.get_matchday_data_for_news("champ1", 5)
    assert data["matchday"] == 5
    assert data["current_standings"][0]["team_id"] == "t1"
    assert data["current_standings"][0]["points_this_matchday"] == 20
    assert "t1" in data["previous_standings"]
    assert data["previous_standings"]["t1"]["position"] == 2
    assert any(bp["player_id"] == "p1" for bp in data["best_players"])
    assert any(tp["player_id"] == "p1" for tp in data["top_players"])
