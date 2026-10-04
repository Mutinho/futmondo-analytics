"""Characterization tests for ``DataSyncService.sync_rosters``.

Freeze the observable behavior across the ``rosters`` extraction
(characterization-first, test-after — see the approved Testing Contract). They
assert the EFFECT: the observable ``SyncResult`` payload (status, keys,
``records_synced``, ``last_sync_matchday``, ``duration_seconds``), the new-round
filtering by matchday, the per-team roster save using ONLY the ``players`` list
(never ``bench``), the per-team recoverable failure (continue, not raise), the
outer failure mode, no credential leak, that ``_find_championship`` is the
injected callable, and the ``sync_all`` key position (``rosters``). Never
``assert True``.

No real DB and no network: deterministic client double + recording port fake +
injected ``find_championship`` stub. ``time.sleep`` monkeypatched to a no-op.
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import app.services.sync.rosters.orchestrator as orch_mod  # noqa: E402
from app.services.data_sync_service import DataSyncService  # noqa: E402
from app.services.sync.rosters import RostersSyncOrchestrator  # noqa: E402

CHAMPIONSHIP_ID = "592416daa3a2dd871a7a9956"


class _RecordingPort:
    def __init__(self, last_sync=None):
        self._last_sync = last_sync
        self.saved = []
        self.metadata = []

    def get_last_sync_metadata(self, championship_id, data_type):
        return self._last_sync

    def save_team_roster(self, championship_id, team_id, roster_players, matchday=None):
        self.saved.append(
            {
                "team_id": team_id,
                "players": list(roster_players),
                "matchday": matchday,
            }
        )

    def update_sync_metadata(self, **kwargs):
        self.metadata.append(kwargs)


class _FakeFutmondoClient:
    """Deterministic double for the client calls rosters sync uses."""

    def __init__(self, standings=None, user_rounds=None, lineups=None, raises=None):
        self._standings = standings
        self._user_rounds = user_rounds or []
        self._lineups = lineups or {}
        self._raises = raises

    def get_matchday_standings(self, championship_id):
        if self._raises is not None:
            raise self._raises
        return self._standings

    def get_userteam_rounds(self, championship_id, team_id):
        return self._user_rounds

    def get_user_roundlineup(self, championship_id, round_id, userteam_id):
        return self._lineups.get((round_id, userteam_id))


def _make_service(monkeypatch, client, port, find_championship):
    def fake_init(self):
        self.dm = object()
        self.championship_id = CHAMPIONSHIP_ID
        self.league_id = ""
        self.user_id = ""
        self.client = client

    monkeypatch.setattr(DataSyncService, "__init__", fake_init)

    def thin_delegation(self):
        orchestrator = RostersSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            find_championship=find_championship,
            data=port,
        )
        return orchestrator.sync()

    monkeypatch.setattr(DataSyncService, "sync_rosters", thin_delegation)
    monkeypatch.setattr(orch_mod.time, "sleep", lambda *a, **k: None)
    return DataSyncService()


# --- Happy path -----------------------------------------------------------
def test_success_saves_only_players_not_bench(monkeypatch):
    """EFFECT: new round rosters saved using ONLY the players list; success."""
    league_data = {"rounds": [{"_id": "r2", "status": "closed"}]}
    client = _FakeFutmondoClient(
        standings={"teams": [{"id": "ut1", "teamid": "tid1"}]},
        user_rounds=[{"id": "r2", "number": 2}],
        lineups={
            ("r2", "ut1"): {
                "players": [{"id": "p1"}, {"id": "p2"}],
                "bench": [{"id": "pb"}],  # must be ignored
            }
        },
    )
    port = _RecordingPort(last_sync={"last_sync_matchday": 1})
    service = _make_service(
        monkeypatch, client, port, find_championship=lambda: (league_data, None)
    )

    result = service.sync_rosters()

    assert result["status"] == "success"
    assert result["records_synced"] == 1
    assert result["last_sync_matchday"] == 2
    assert isinstance(result["duration_seconds"], float)
    assert len(port.saved) == 1
    saved = port.saved[0]
    assert saved["team_id"] == "tid1"
    assert saved["matchday"] == 2
    # Only the players list is persisted — bench excluded.
    assert [p["id"] for p in saved["players"]] == ["p1", "p2"]
    assert port.metadata[0]["sync_status"] == "success"
    assert port.metadata[0]["data_type"] == "rosters"


def test_first_sync_with_no_rounds_is_success(monkeypatch):
    """EFFECT: last_matchday==0 forces success even with zero rosters synced."""
    client = _FakeFutmondoClient(standings={"teams": []}, user_rounds=[], lineups={})
    port = _RecordingPort(last_sync=None)
    service = _make_service(
        monkeypatch, client, port, find_championship=lambda: (None, None)
    )

    result = service.sync_rosters()

    assert result["status"] == "success"
    assert result["records_synced"] == 0
    assert result["last_sync_matchday"] == 0
    assert port.saved == []


def test_no_new_rounds_with_prior_matchday_is_no_new_data(monkeypatch):
    """EFFECT: all rounds already synced + prior matchday -> no_new_data."""
    league_data = {"rounds": [{"_id": "r1", "status": "closed"}]}
    client = _FakeFutmondoClient(
        standings={"teams": [{"id": "ut1", "teamid": "tid1"}]},
        user_rounds=[{"id": "r1", "number": 1}],
        lineups={},
    )
    port = _RecordingPort(last_sync={"last_sync_matchday": 5})
    service = _make_service(
        monkeypatch, client, port, find_championship=lambda: (league_data, None)
    )

    result = service.sync_rosters()

    assert result["status"] == "no_new_data"
    assert result["records_synced"] == 0
    assert result["last_sync_matchday"] == 5


def test_per_team_failure_is_recoverable_continue(monkeypatch):
    """EFFECT: a lineup fetch failure for one team is caught (continue)."""

    class _FailingLineupClient(_FakeFutmondoClient):
        def get_user_roundlineup(self, championship_id, round_id, userteam_id):
            raise RuntimeError("lineup fetch failed")

    league_data = {"rounds": [{"_id": "r2", "status": "closed"}]}
    client = _FailingLineupClient(
        standings={"teams": [{"id": "ut1", "teamid": "tid1"}]},
        user_rounds=[{"id": "r2", "number": 2}],
    )
    port = _RecordingPort(last_sync={"last_sync_matchday": 1})
    service = _make_service(
        monkeypatch, client, port, find_championship=lambda: (league_data, None)
    )

    result = service.sync_rosters()

    # The team failed and was skipped; prior matchday -> no_new_data, not error.
    assert result["status"] == "no_new_data"
    assert result["records_synced"] == 0
    assert port.saved == []


# --- Failure modes --------------------------------------------------------
def test_outer_exception_is_error(monkeypatch):
    """EFFECT: an exception from the injected find_championship -> status error."""

    def exploding_find():
        raise RuntimeError("league list failed")

    client = _FakeFutmondoClient(standings={"teams": []})
    port = _RecordingPort(last_sync={"last_sync_matchday": 3})
    service = _make_service(monkeypatch, client, port, find_championship=exploding_find)

    result = service.sync_rosters()

    assert result["status"] == "error"
    assert "league list failed" in result["error"]
    assert "duration_seconds" in result
    assert port.metadata[0]["sync_status"] == "error"


def test_error_message_carries_no_credentials(monkeypatch):
    """EFFECT (BR4.2): the error payload never leaks the Futmondo password/token."""

    def exploding_find():
        raise RuntimeError("timeout on /leagueList")

    client = _FakeFutmondoClient(standings={"teams": []})
    port = _RecordingPort(last_sync={"last_sync_matchday": 3})
    service = _make_service(monkeypatch, client, port, find_championship=exploding_find)

    result = service.sync_rosters()

    assert result["status"] == "error"
    assert "password" not in result["error"].lower()
    assert "token" not in result["error"].lower()


def test_find_championship_is_the_injected_callable(monkeypatch):
    """EFFECT (BR2.3): the orchestrator calls the injected find_championship once."""
    calls = {"n": 0}

    def spy_find():
        calls["n"] += 1
        return (None, None)

    client = _FakeFutmondoClient(standings={"teams": []})
    port = _RecordingPort(last_sync=None)
    service = _make_service(monkeypatch, client, port, find_championship=spy_find)

    service.sync_rosters()

    assert calls["n"] == 1


# --- sync_all ordering ----------------------------------------------------
def test_sync_all_keeps_rosters_key_in_order(monkeypatch):
    """EFFECT (BR3.1): sync_all keeps the literal ``rosters`` key in position."""
    port = _RecordingPort()
    service = _make_service(
        monkeypatch, _FakeFutmondoClient(), port, find_championship=lambda: (None, None)
    )

    sentinels = {}
    for name in (
        "sync_players_full",
        "sync_transactions",
        "sync_clauses",
        "sync_punishments_bonuses",
        "sync_dream_teams_mvps",
        "sync_player_performance",
        "sync_rosters",
        "sync_round_rankings",
        "sync_match_odds",
        "sync_prizes",
    ):
        marker = {"status": f"stub-{name}"}
        sentinels[name] = marker
        monkeypatch.setattr(service, name, (lambda m=marker: m))

    results = service.sync_all()

    assert "rosters" in results
    assert results["rosters"] == sentinels["sync_rosters"]
    keys = list(results.keys())
    assert keys.index("rosters") == 6
    assert len(keys) == 10
    assert keys[-1] == "prizes"
