"""Characterization safety net for the ``dream-teams-mvp`` responsibility (rank 6).

Freezes the observable effect of ``save_dream_team_mvp`` /
``get_dream_team_bonus_stats`` over the in-memory fake (BR2.1/BR3.1). Asserts the
effect — rows written with is_mvp flag, player-existence gating, bonus counts via
the roster join — never ``assert True`` (BR2.2/BR2.3). No network/DB/credentials.
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
        cursor.execute("CREATE TABLE IF NOT EXISTS players (player_id TEXT PRIMARY KEY, name TEXT)")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dream_teams_mvps (
                championship_id TEXT, round_id TEXT, matchday INTEGER, player_id TEXT,
                is_mvp INTEGER, recorded_at TEXT,
                PRIMARY KEY (championship_id, round_id, player_id, is_mvp)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS team_rosters (
                championship_id TEXT, team_id TEXT, matchday INTEGER, player_id TEXT
            )
            """
        )
        for pid in ("p1", "p2", "pmvp"):
            cursor.execute("INSERT INTO players (player_id, name) VALUES (?, ?)", (pid, pid))
    return dm


def _count_rows(fake_db, is_mvp):
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("SELECT COUNT(*) FROM dream_teams_mvps WHERE is_mvp = ?", (is_mvp,))
        return cursor.fetchone()[0]


def test_save_dream_team_mvp_writes_members_and_mvp(fake_db):
    dm = _make_dm(fake_db)
    dm.save_dream_team_mvp("champ1", "r1", 5, ["p1", "p2"], mvp_player_id="pmvp")
    assert _count_rows(fake_db, 0) == 2  # two dream-team members
    assert _count_rows(fake_db, 1) == 1  # one MVP


def test_save_dream_team_skips_unknown_player_without_details(fake_db):
    dm = _make_dm(fake_db)
    dm.save_dream_team_mvp("champ1", "r1", 5, ["ghost"], mvp_player_id=None)
    assert _count_rows(fake_db, 0) == 0


def test_save_dream_team_empty_is_noop(fake_db):
    dm = _make_dm(fake_db)
    dm.save_dream_team_mvp("champ1", "r1", 5, [], mvp_player_id=None)
    assert _count_rows(fake_db, 0) == 0
    assert _count_rows(fake_db, 1) == 0


def test_get_dream_team_bonus_stats_counts_per_team(fake_db):
    dm = _make_dm(fake_db)
    dm.save_dream_team_mvp("champ1", "r1", 5, ["p1", "p2"], mvp_player_id="pmvp")
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("INSERT INTO team_rosters VALUES (?, ?, ?, ?)", ("champ1", "teamA", 5, "p1"))
        cursor.execute(
            "INSERT INTO team_rosters VALUES (?, ?, ?, ?)", ("champ1", "teamA", 5, "pmvp")
        )
    stats = dm.get_dream_team_bonus_stats("champ1")
    assert stats["teamA"]["ideal_team_count"] == 1
    assert stats["teamA"]["mvp_count"] == 1


def test_get_dream_team_bonus_stats_empty_championship(fake_db):
    dm = _make_dm(fake_db)
    assert dm.get_dream_team_bonus_stats("nope") == {}
