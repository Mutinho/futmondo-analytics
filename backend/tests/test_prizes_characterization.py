"""Characterization tests for prize PRODUCTION in ``sync_prizes`` (safety net).

These tests freeze the CURRENT observable behavior of the prize-production side
of ``DataSyncService.sync_prizes`` before the tie-splitting improvement is
implemented (characterization-first, test-after — see the approved Testing
Contract). They exercise every branch called out by the team practices (Q2=A):

  * ``points_prize`` — always paid,
  * gating ``round_fully_played`` (a "closed" round with unfinished matches),
  * ranking ``flop`` and ``top`` modes,
  * MVP prize,
  * dream-team prize,
  * advanced pseudo-round (synthetic negative matchday, points only),
  * defensive ``DELETE ... NOT IN`` cleanup of stale matchdays.

They also freeze the CURRENT tie bug: two teams tied on points receive prizes
of DIFFERENT positions today. That test is marked as the deliberate,
traceable behavior change point for the new-contract phase (Step 6).

No real DB and no network: the Futmondo API client is a deterministic double
and persistence uses the shared in-memory ``fake_db`` fixture (``conftest.py``),
which exercises the real parameterized SQL (UPSERT + ``DELETE ... NOT IN``).
``time.sleep`` is monkeypatched to a no-op so no wall-clock time is spent.
"""

import os

# ``app.core.config`` hardens JWT startup (NFR1.1): set a non-default secret
# BEFORE importing the app so instantiating the service does not fail at import.
os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import app.services.data_sync_service as dss  # noqa: E402
import app.services.db_connection as db_connection  # noqa: E402
from app.services.data_sync_service import DataSyncService  # noqa: E402

CHAMPIONSHIP_ID = "592416daa3a2dd871a7a9956"

# Column order of the ``team_prizes`` rows written by ``sync_prizes``.
_COLS = (
    "championship_id", "team_id", "matchday",
    "ranking_prize", "mvp_prize", "position",
    "points_prize", "dream_team_prize",
)


class _FakeFutmondoClient:
    """Deterministic double of the Futmondo API client used by ``sync_prizes``.

    Every response is fixed data supplied per test; no network and no sleeps.
    Only the methods ``sync_prizes`` calls are implemented.
    """

    def __init__(self, *, standings, rounds, matches_by_round=None,
                 ranking_by_matchday=None, dream_team=None,
                 lineup_by_team=None):
        self._standings = standings
        self._rounds = rounds
        self._matches_by_round = matches_by_round or {}
        self._ranking_by_matchday = ranking_by_matchday or {}
        self._dream_team = dream_team
        self._lineup_by_team = lineup_by_team or {}

    def get_matchday_standings(self, championship_id, matchday=None):
        return self._standings

    def get_userteam_rounds(self, championship_id, user_team_id):
        return self._rounds

    def get_round_matches(self, championship_id, round_id, userteam_id):
        return self._matches_by_round.get(round_id, {"matches": []})

    def get_round_ranking(self, championship_id, round_number, round_id,
                          userteam_id):
        return self._ranking_by_matchday.get(round_number, [])

    def get_dream_team(self, championship_id, round_id=None, matchday=None):
        return self._dream_team

    def get_round_lineup(self, championship_id, round_id, userteam_id):
        return self._lineup_by_team.get(userteam_id, [])


def _prepare_db(fake_db, config_row):
    """Create the tables ``sync_prizes`` touches and seed the config row.

    ``NOW()`` is registered on the SQLite connection because the production
    UPSERT calls it and SQLite has no such builtin.
    """
    fake_db._conn.create_function("NOW", 0, lambda: "2026-01-01T00:00:00")
    cur = fake_db._conn.cursor()
    cur.execute(
        """CREATE TABLE user_championships (
               championship_id TEXT,
               money_per_ranking INTEGER, mvp_bonus INTEGER,
               ranking_mode TEXT, users_to_rank INTEGER,
               money_per_point INTEGER, dream_team_bonus INTEGER)"""
    )
    cur.execute(
        """INSERT INTO user_championships
               (championship_id, money_per_ranking, mvp_bonus, ranking_mode,
                users_to_rank, money_per_point, dream_team_bonus)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (CHAMPIONSHIP_ID, *config_row),
    )
    cur.execute(
        """CREATE TABLE team_prizes (
               championship_id TEXT, team_id TEXT, matchday INTEGER,
               ranking_prize INTEGER, mvp_prize INTEGER, position INTEGER,
               points_prize INTEGER, dream_team_prize INTEGER,
               synced_at TEXT,
               PRIMARY KEY (championship_id, team_id, matchday))"""
    )
    fake_db._conn.commit()


def _make_service(monkeypatch, fake_db, client):
    """Build a ``DataSyncService`` with fakes, avoiding real DB/network init."""

    def fake_init(self):
        self.dm = None  # sync_prizes uses get_db(), not self.dm
        self.championship_id = CHAMPIONSHIP_ID
        self.league_id = ""
        self.user_id = ""
        self.client = client

    monkeypatch.setattr(DataSyncService, "__init__", fake_init)
    monkeypatch.setattr(db_connection, "get_db", lambda: fake_db)
    monkeypatch.setattr(dss.time, "sleep", lambda *a, **k: None)
    return DataSyncService()


def _stored_rows(fake_db):
    """Return the persisted ``team_prizes`` rows as dicts (matchday order)."""
    cur = fake_db._conn.cursor()
    cur.execute(
        "SELECT championship_id, team_id, matchday, ranking_prize, mvp_prize, "
        "position, points_prize, dream_team_prize FROM team_prizes "
        "ORDER BY matchday, team_id"
    )
    return [dict(zip(_COLS, row)) for row in cur.fetchall()]


def _by_team(rows):
    return {r["team_id"]: r for r in rows}


# --- Shared deterministic builders ------------------------------------------

def _standings(team_ids):
    return {"teams": [{"teamid": tid} for tid in team_ids]}


def _closed_round(round_id="r1", number=5):
    return [{"id": round_id, "number": number, "status": "closed"}]


def _all_finished(*, n=2):
    return {"matches": [{"status": "F"} for _ in range(n)]}


# ---------------------------------------------------------------------------
# Characterization tests
# ---------------------------------------------------------------------------

def test_points_prize_always_paid_even_when_round_not_fully_played(
        fake_db, monkeypatch):
    """points_prize is paid for a 'closed' round with unfinished matches;
    ranking/MVP/dream-team are gated to 0 (round_fully_played is False)."""
    _prepare_db(fake_db, config_row=(3_000_000, 0, "flop", -1, 1_000, 0))
    client = _FakeFutmondoClient(
        standings=_standings(["A", "B"]),
        rounds=_closed_round(),
        matches_by_round={"r1": {"matches": [
            {"status": "F"}, {"status": "P"},  # one postponed -> not fully played
        ]}},
        ranking_by_matchday={5: [
            {"id": "A", "points": 100, "position": 1},
            {"id": "B", "points": 80, "position": 2},
        ]},
    )
    service = _make_service(monkeypatch, fake_db, client)

    result = service.sync_prizes()

    assert result["status"] == "success"
    rows = _by_team(_stored_rows(fake_db))
    # points_prize = round(points * money_per_point)
    assert rows["A"]["points_prize"] == 100_000
    assert rows["B"]["points_prize"] == 80_000
    # ranking gated off because the round is not fully played
    assert rows["A"]["ranking_prize"] == 0
    assert rows["B"]["ranking_prize"] == 0


def test_ranking_flop_mode_prize_per_position(fake_db, monkeypatch):
    """flop mode: ratio(pos) = pos / total_pct; prize = round(money * ratio)."""
    _prepare_db(fake_db, config_row=(3_000_000, 0, "flop", -1, 0, 0))
    client = _FakeFutmondoClient(
        standings=_standings(["A", "B", "C", "D"]),
        rounds=_closed_round(),
        matches_by_round={"r1": _all_finished()},
        ranking_by_matchday={5: [
            {"id": "A", "points": 100, "position": 1},
            {"id": "B", "points": 90, "position": 2},
            {"id": "C", "points": 80, "position": 3},
            {"id": "D", "points": 70, "position": 4},
        ]},
    )
    service = _make_service(monkeypatch, fake_db, client)

    service.sync_prizes()

    rows = _by_team(_stored_rows(fake_db))
    # active_members = 4, total_pct = 4*5/2 = 10
    # flop ratio = pos/10 -> pos1=300000, pos2=600000, pos3=900000, pos4=1200000
    assert rows["A"]["ranking_prize"] == 300_000
    assert rows["B"]["ranking_prize"] == 600_000
    assert rows["C"]["ranking_prize"] == 900_000
    assert rows["D"]["ranking_prize"] == 1_200_000


def test_ranking_top_mode_prize_per_position(fake_db, monkeypatch):
    """top mode: ratio(pos) = (active_members - pos + 1) / total_pct."""
    _prepare_db(fake_db, config_row=(3_000_000, 0, "top", -1, 0, 0))
    client = _FakeFutmondoClient(
        standings=_standings(["A", "B", "C", "D"]),
        rounds=_closed_round(),
        matches_by_round={"r1": _all_finished()},
        ranking_by_matchday={5: [
            {"id": "A", "points": 100, "position": 1},
            {"id": "B", "points": 90, "position": 2},
            {"id": "C", "points": 80, "position": 3},
            {"id": "D", "points": 70, "position": 4},
        ]},
    )
    service = _make_service(monkeypatch, fake_db, client)

    service.sync_prizes()

    rows = _by_team(_stored_rows(fake_db))
    # top ratio = (4 - pos + 1)/10 -> pos1=1200000, pos2=900000, pos3=600000, pos4=300000
    assert rows["A"]["ranking_prize"] == 1_200_000
    assert rows["B"]["ranking_prize"] == 900_000
    assert rows["C"]["ranking_prize"] == 600_000
    assert rows["D"]["ranking_prize"] == 300_000


def test_mvp_prize_awarded_to_team_with_mvp_player(fake_db, monkeypatch):
    """MVP bonus goes to the team whose lineup contains the MVP player."""
    _prepare_db(fake_db, config_row=(0, 5_000_000, "flop", -1, 0, 0))
    client = _FakeFutmondoClient(
        standings=_standings(["A", "B"]),
        rounds=_closed_round(),
        matches_by_round={"r1": _all_finished()},
        ranking_by_matchday={5: [
            {"id": "A", "points": 100, "position": 1},
            {"id": "B", "points": 80, "position": 2},
        ]},
        dream_team={"mvp": "player-99", "players": []},
        lineup_by_team={
            "A": [{"id": "player-1"}],
            "B": [{"id": "player-99"}],  # team B has the MVP
        },
    )
    service = _make_service(monkeypatch, fake_db, client)

    service.sync_prizes()

    rows = _by_team(_stored_rows(fake_db))
    assert rows["B"]["mvp_prize"] == 5_000_000
    assert rows["A"]["mvp_prize"] == 0


def test_dream_team_prize_counts_players_per_team(fake_db, monkeypatch):
    """dream_team_prize = round(count_of_dream_team_players * dream_team_bonus)."""
    _prepare_db(fake_db, config_row=(0, 0, "flop", -1, 0, 1_000_000))
    client = _FakeFutmondoClient(
        standings=_standings(["A", "B"]),
        rounds=_closed_round(),
        matches_by_round={"r1": _all_finished()},
        ranking_by_matchday={5: [
            {"id": "A", "points": 100, "position": 1},
            {"id": "B", "points": 80, "position": 2},
        ]},
        dream_team={"mvp": None, "players": [{"id": "p1"}, {"id": "p2"}, {"id": "p3"}]},
        lineup_by_team={
            "A": [{"id": "p1"}, {"id": "p2"}],  # 2 dream-team players
            "B": [{"id": "p3"}],                # 1 dream-team player
        },
    )
    service = _make_service(monkeypatch, fake_db, client)

    service.sync_prizes()

    rows = _by_team(_stored_rows(fake_db))
    assert rows["A"]["dream_team_prize"] == 2_000_000
    assert rows["B"]["dream_team_prize"] == 1_000_000


def test_advanced_pseudo_round_stored_as_negative_matchday_points_only(
        fake_db, monkeypatch):
    """A non-integer round number (0.5) is stored under synthetic matchday -5
    and pays points_prize only (ranking/MVP/dream-team gated off)."""
    _prepare_db(fake_db, config_row=(3_000_000, 5_000_000, "flop", -1, 1_000, 0))
    client = _FakeFutmondoClient(
        standings=_standings(["A", "B"]),
        rounds=[{"id": "r-adv", "number": 0.5, "status": "closed"}],
        matches_by_round={},  # not consulted for pseudo-rounds
        ranking_by_matchday={-5: [
            {"id": "A", "points": 100, "position": 1},
            {"id": "B", "points": 80, "position": 2},
        ]},
    )
    service = _make_service(monkeypatch, fake_db, client)

    service.sync_prizes()

    rows = _stored_rows(fake_db)
    assert all(r["matchday"] == -5 for r in rows)
    by_team = _by_team(rows)
    assert by_team["A"]["points_prize"] == 100_000
    # ranking/MVP gated off for advanced pseudo-round
    assert by_team["A"]["ranking_prize"] == 0
    assert by_team["A"]["mvp_prize"] == 0


def test_defensive_delete_removes_stale_matchdays(fake_db, monkeypatch):
    """A pre-existing prize row for a matchday no longer reported is deleted
    by the defensive DELETE ... NOT IN cleanup after the sync."""
    _prepare_db(fake_db, config_row=(3_000_000, 0, "flop", -1, 1_000, 0))
    # Seed a stale row for matchday 99 that the current sync will not re-report.
    cur = fake_db._conn.cursor()
    cur.execute(
        "INSERT INTO team_prizes (championship_id, team_id, matchday, "
        "ranking_prize, mvp_prize, position, points_prize, dream_team_prize, "
        "synced_at) VALUES (?, ?, ?, 0, 0, 1, 0, 0, NOW())",
        (CHAMPIONSHIP_ID, "A", 99),
    )
    fake_db._conn.commit()

    client = _FakeFutmondoClient(
        standings=_standings(["A", "B"]),
        rounds=_closed_round(),
        matches_by_round={"r1": _all_finished()},
        ranking_by_matchday={5: [
            {"id": "A", "points": 100, "position": 1},
            {"id": "B", "points": 80, "position": 2},
        ]},
    )
    service = _make_service(monkeypatch, fake_db, client)

    result = service.sync_prizes()

    assert result["stale_prizes_removed"] == 1
    matchdays = {r["matchday"] for r in _stored_rows(fake_db)}
    assert matchdays == {5}  # matchday 99 removed


def test_tie_split_corrected_behavior_equal_prizes_for_tied_teams(
        fake_db, monkeypatch):
    """DELIBERATE, TRACEABLE CONTRACT CHANGE (was the frozen tie bug).

    This test previously froze the tie BUG: two teams tied on the same
    round_points received prizes of DIFFERENT positions, dependent on the
    arbitrary API order. Step 4 of this intent (FR1 / BR3.1) corrected that:
    the two positions the tie group occupies are summed and split equally.
    Per the Testing Contract (Q3=C), the phase-1 test that described the wrong
    behavior is updated here to describe the CORRECT behavior — an intentional
    change of contract, not a regression. See test_prizes_calculator.py for the
    unit-level tie tests, including the referenced jornada-5 example.
    """
    _prepare_db(fake_db, config_row=(3_000_000, 0, "flop", -1, 0, 0))
    # A and B are tied on 80 points, occupying positions 3 and 4 (flop mode).
    client = _FakeFutmondoClient(
        standings=_standings(["W", "X", "A", "B"]),
        rounds=_closed_round(),
        matches_by_round={"r1": _all_finished()},
        ranking_by_matchday={5: [
            {"id": "W", "points": 100, "position": 1},
            {"id": "X", "points": 90, "position": 2},
            {"id": "A", "points": 80, "position": 3},
            {"id": "B", "points": 80, "position": 4},  # tied with A
        ]},
    )
    service = _make_service(monkeypatch, fake_db, client)

    service.sync_prizes()

    rows = _by_team(_stored_rows(fake_db))
    # total_pct = 4*5/2 = 10; flop prize(3) = round(3M*3/10) = 900000,
    # prize(4) = round(3M*4/10) = 1200000. Sum = 2100000, split by 2 ->
    # round(2100000/2) = 1050000 each. The result no longer depends on the
    # arbitrary API order among the tied teams.
    assert rows["A"]["ranking_prize"] == 1_050_000
    assert rows["B"]["ranking_prize"] == 1_050_000
    # Non-tied teams keep their exact single-position prize (no regression).
    assert rows["W"]["ranking_prize"] == 300_000
    assert rows["X"]["ranking_prize"] == 600_000
