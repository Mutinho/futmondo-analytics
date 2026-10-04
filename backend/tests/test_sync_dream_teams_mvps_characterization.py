"""Characterization tests for ``DataSyncService.sync_dream_teams_mvps``.

Freeze the observable behavior across the ``dream_teams_mvps`` extraction
(characterization-first, test-after — see the approved Testing Contract). They
assert the EFFECT: the observable ``SyncResult`` payload (status, keys,
``records_synced``, ``last_sync_matchday``, ``duration_seconds``), the
new-round filtering by matchday, the dream-team player/MVP extraction, the
``save_dream_team_mvp`` arguments (including ``player_details``), the
per-round recoverable failure (continue, not raise), the outer failure mode,
no credential leak, that ``_find_championship`` is the injected callable, and the
``sync_all`` key position (``dream_teams``). Never ``assert True``.

No real DB and no network: deterministic client double + recording port fake +
injected ``find_championship`` stub. ``time.sleep`` monkeypatched to a no-op.
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import app.services.sync.dream_teams_mvps.orchestrator as orch_mod  # noqa: E402
from app.services.data_sync_service import DataSyncService  # noqa: E402
from app.services.sync.dream_teams_mvps import (  # noqa: E402
    DreamTeamsMvpsSyncOrchestrator,
)

CHAMPIONSHIP_ID = "592416daa3a2dd871a7a9956"


class _RecordingPort:
    def __init__(self, last_sync=None):
        self._last_sync = last_sync
        self.saved = []
        self.metadata = []

    def get_last_sync_metadata(self, championship_id, data_type):
        return self._last_sync

    def save_dream_team_mvp(
        self, championship_id, round_id, matchday, dream_team_players, mvp_id,
        player_details=None,
    ):
        self.saved.append(
            {
                "round_id": round_id,
                "matchday": matchday,
                "players": list(dream_team_players),
                "mvp_id": mvp_id,
                "player_details": player_details,
            }
        )

    def update_sync_metadata(self, **kwargs):
        self.metadata.append(kwargs)


class _FakeFutmondoClient:
    """Deterministic double for the three client calls dream-teams sync uses."""

    def __init__(self, standings=None, user_rounds=None, dream_teams=None, raises=None):
        self._standings = standings
        self._user_rounds = user_rounds or []
        self._dream_teams = dream_teams or {}
        self._raises = raises

    def get_matchday_standings(self, championship_id):
        if self._raises is not None:
            raise self._raises
        return self._standings

    def get_userteam_rounds(self, championship_id, team_id):
        return self._user_rounds

    def get_dream_team(self, championship_id, round_id=None):
        return self._dream_teams.get(round_id)


def _make_service(monkeypatch, client, port, find_championship):
    def fake_init(self):
        self.dm = object()
        self.championship_id = CHAMPIONSHIP_ID
        self.league_id = ""
        self.user_id = ""
        self.client = client

    monkeypatch.setattr(DataSyncService, "__init__", fake_init)

    def thin_delegation(self):
        orchestrator = DreamTeamsMvpsSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            find_championship=find_championship,
            data=port,
        )
        return orchestrator.sync()

    monkeypatch.setattr(DataSyncService, "sync_dream_teams_mvps", thin_delegation)
    monkeypatch.setattr(orch_mod.time, "sleep", lambda *a, **k: None)
    return DataSyncService()


# --- Happy path -----------------------------------------------------------
def test_success_syncs_new_closed_rounds(monkeypatch):
    """EFFECT: a new closed round yields a saved dream team + MVP, status success."""
    league_data = {
        "rounds": [
            {"_id": "r1", "status": "closed"},
            {"_id": "r2", "status": "closed"},
        ]
    }
    client = _FakeFutmondoClient(
        standings={"teams": [{"id": "team-sample"}]},
        user_rounds=[{"id": "r1", "number": 1}, {"id": "r2", "number": 2}],
        dream_teams={
            "r1": {"players": [{"id": "p1"}, {"id": "p2"}], "mvp": "p1"},
            "r2": {"players": [{"id": "p3"}], "mvp": "p3"},
        },
    )
    port = _RecordingPort(last_sync={"last_sync_matchday": 1})
    service = _make_service(
        monkeypatch, client, port, find_championship=lambda: (league_data, None)
    )

    result = service.sync_dream_teams_mvps()

    assert result["status"] == "success"
    # Only round 2 is after last_matchday=1 -> one round synced.
    assert result["records_synced"] == 1
    assert result["last_sync_matchday"] == 2
    assert isinstance(result["duration_seconds"], float)
    assert len(port.saved) == 1
    saved = port.saved[0]
    assert saved["round_id"] == "r2"
    assert saved["matchday"] == 2
    assert saved["players"] == ["p3"]
    assert saved["mvp_id"] == "p3"
    # player_details carries the dict form keyed by player id.
    assert saved["player_details"] == {"p3": {"id": "p3"}}
    assert port.metadata[0]["sync_status"] == "success"
    assert port.metadata[0]["data_type"] == "dream_teams"
    assert port.metadata[0]["last_sync_matchday"] == 2


def test_first_sync_with_no_new_rounds_is_success(monkeypatch):
    """EFFECT: last_matchday==0 forces success even with zero rounds synced."""
    client = _FakeFutmondoClient(standings={"teams": []}, user_rounds=[], dream_teams={})
    port = _RecordingPort(last_sync=None)  # last_matchday resolves to 0
    service = _make_service(
        monkeypatch, client, port, find_championship=lambda: (None, None)
    )

    result = service.sync_dream_teams_mvps()

    assert result["status"] == "success"
    assert result["records_synced"] == 0
    assert result["last_sync_matchday"] == 0
    assert port.saved == []


def test_no_new_rounds_with_prior_matchday_is_no_new_data(monkeypatch):
    """EFFECT: all rounds already synced + prior matchday -> no_new_data."""
    league_data = {"rounds": [{"_id": "r1", "status": "closed"}]}
    client = _FakeFutmondoClient(
        standings={"teams": [{"id": "s"}]},
        user_rounds=[{"id": "r1", "number": 1}],
        dream_teams={},
    )
    port = _RecordingPort(last_sync={"last_sync_matchday": 5})
    service = _make_service(
        monkeypatch, client, port, find_championship=lambda: (league_data, None)
    )

    result = service.sync_dream_teams_mvps()

    assert result["status"] == "no_new_data"
    assert result["records_synced"] == 0
    assert result["last_sync_matchday"] == 5


def test_per_round_failure_is_recoverable_continue(monkeypatch):
    """EFFECT: a dream-team fetch failure for one round is caught (continue)."""

    class _FailingDreamClient(_FakeFutmondoClient):
        def get_dream_team(self, championship_id, round_id=None):
            raise RuntimeError("dream fetch failed")

    league_data = {"rounds": [{"_id": "r2", "status": "closed"}]}
    client = _FailingDreamClient(
        standings={"teams": [{"id": "s"}]},
        user_rounds=[{"id": "r2", "number": 2}],
    )
    port = _RecordingPort(last_sync={"last_sync_matchday": 1})
    service = _make_service(
        monkeypatch, client, port, find_championship=lambda: (league_data, None)
    )

    result = service.sync_dream_teams_mvps()

    # The round failed and was skipped; with prior matchday this is no_new_data,
    # NOT an error (the per-round except continues).
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
    service = _make_service(
        monkeypatch, client, port, find_championship=exploding_find
    )

    result = service.sync_dream_teams_mvps()

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
    service = _make_service(
        monkeypatch, client, port, find_championship=exploding_find
    )

    result = service.sync_dream_teams_mvps()

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

    service.sync_dream_teams_mvps()

    assert calls["n"] == 1


# --- sync_all ordering ----------------------------------------------------
def test_sync_all_keeps_dream_teams_key_in_order(monkeypatch):
    """EFFECT (BR3.1): sync_all keeps the literal ``dream_teams`` key in position."""
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

    assert "dream_teams" in results
    assert results["dream_teams"] == sentinels["sync_dream_teams_mvps"]
    keys = list(results.keys())
    assert keys.index("dream_teams") == 4
    assert len(keys) == 10
    assert keys[-1] == "prizes"
