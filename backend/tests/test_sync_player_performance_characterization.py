"""Characterization tests for ``DataSyncService.sync_player_performance``.

Freeze the observable behavior across the ``player_performance`` extraction
(characterization-first, test-after — see the approved Testing Contract). They
assert the EFFECT: the observable ``SyncResult`` payload (status, keys,
``records_synced``, ``last_sync_matchday``, ``duration_seconds``), the
no-teams / no-round-map early ``no_new_data`` branches (which still write
metadata), the per-matchday per-team batch save, the points/value/best-player
extraction with fallbacks, the per-team recoverable failure (continue), the
outer failure mode, no credential leak, and the ``sync_all`` key position
(``player_performance``). Never ``assert True``.

No real DB and no network: deterministic client double + recording port fake.
``time.sleep`` monkeypatched to a no-op. No credentials appear anywhere.
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import app.services.sync.player_performance.orchestrator as orch_mod  # noqa: E402
from app.services.data_sync_service import DataSyncService  # noqa: E402
from app.services.sync.player_performance import (  # noqa: E402
    PlayerPerformanceSyncOrchestrator,
)

CHAMPIONSHIP_ID = "592416daa3a2dd871a7a9956"


class _RecordingPort:
    def __init__(self, last_sync=None):
        self._last_sync = last_sync
        self.saved = []
        self.metadata = []

    def get_last_sync_metadata(self, championship_id, data_type):
        return self._last_sync

    def save_player_performance_batch(self, championship_id, records):
        self.saved.append({"championship_id": championship_id, "records": list(records)})

    def update_sync_metadata(self, **kwargs):
        self.metadata.append(kwargs)


class _FakeFutmondoClient:
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


def _make_service(monkeypatch, client, port):
    def fake_init(self):
        self.dm = object()
        self.championship_id = CHAMPIONSHIP_ID
        self.league_id = ""
        self.user_id = ""
        self.client = client

    monkeypatch.setattr(DataSyncService, "__init__", fake_init)

    def thin_delegation(self):
        orchestrator = PlayerPerformanceSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            data=port,
        )
        return orchestrator.sync()

    monkeypatch.setattr(DataSyncService, "sync_player_performance", thin_delegation)
    monkeypatch.setattr(orch_mod.time, "sleep", lambda *a, **k: None)
    return DataSyncService()


# --- Happy path -----------------------------------------------------------
def test_success_extracts_points_value_and_best_player(monkeypatch):
    """EFFECT: a lineup is batch-saved with extracted points/value/best-player flags."""
    client = _FakeFutmondoClient(
        standings={"teams": [{"id": "ut1", "teamid": "tid1"}]},
        user_rounds=[{"id": "r1", "number": 1}],
        lineups={
            ("r1", "ut1"): {
                "players": [
                    {"id": "p1", "points": 7, "value": 1000, "bestPlayer": True},
                    {"id": "p2", "score": 3, "marketValue": 500},
                    {"id": "p3"},  # no points -> skipped
                ]
            }
        },
    )
    port = _RecordingPort(last_sync={"last_sync_matchday": 0})
    service = _make_service(monkeypatch, client, port)

    result = service.sync_player_performance()

    assert result["status"] == "success"
    assert result["records_synced"] == 2  # p3 skipped (no points)
    assert result["last_sync_matchday"] == 1
    assert isinstance(result["duration_seconds"], float)
    assert len(port.saved) == 1
    recs = {r["player_id"]: r for r in port.saved[0]["records"]}
    assert recs["p1"]["points"] == 7
    assert recs["p1"]["value"] == 1000
    assert recs["p1"]["was_best_player"] is True
    assert recs["p1"]["team_id"] == "tid1"
    assert recs["p2"]["points"] == 3  # from the ``score`` fallback
    assert recs["p2"]["value"] == 500  # from ``marketValue`` fallback
    assert recs["p2"]["was_best_player"] is False
    assert port.metadata[0]["sync_status"] == "success"
    assert port.metadata[0]["data_type"] == "player_performance"


def test_no_teams_is_no_new_data_and_writes_metadata(monkeypatch):
    """EFFECT: empty team map -> early no_new_data branch still writes metadata."""
    client = _FakeFutmondoClient(standings={"teams": []})
    port = _RecordingPort(last_sync={"last_sync_matchday": 4})
    service = _make_service(monkeypatch, client, port)

    result = service.sync_player_performance()

    assert result["status"] == "no_new_data"
    assert result["records_synced"] == 0
    assert result["last_sync_matchday"] == 4
    assert port.saved == []
    assert len(port.metadata) == 1
    assert port.metadata[0]["sync_status"] == "no_new_data"
    assert port.metadata[0]["last_sync_matchday"] == 4


def test_no_round_map_is_no_new_data_and_writes_metadata(monkeypatch):
    """EFFECT: no usable round mapping -> early no_new_data branch writes metadata."""
    client = _FakeFutmondoClient(
        standings={"teams": [{"id": "ut1", "teamid": "tid1"}]},
        user_rounds=[],  # no round mapping
    )
    port = _RecordingPort(last_sync={"last_sync_matchday": 2})
    service = _make_service(monkeypatch, client, port)

    result = service.sync_player_performance()

    assert result["status"] == "no_new_data"
    assert result["records_synced"] == 0
    assert result["last_sync_matchday"] == 2
    assert port.saved == []
    assert len(port.metadata) == 1


def test_per_team_failure_is_recoverable_continue(monkeypatch):
    """EFFECT: a lineup fetch failure for one team is caught (continue)."""

    class _FailingClient(_FakeFutmondoClient):
        def get_user_roundlineup(self, championship_id, round_id, userteam_id):
            raise RuntimeError("lineup fetch failed")

    client = _FailingClient(
        standings={"teams": [{"id": "ut1", "teamid": "tid1"}]},
        user_rounds=[{"id": "r1", "number": 1}],
    )
    port = _RecordingPort(last_sync={"last_sync_matchday": 0})
    service = _make_service(monkeypatch, client, port)

    result = service.sync_player_performance()

    assert result["status"] == "no_new_data"
    assert result["records_synced"] == 0
    assert port.saved == []


# --- Failure modes --------------------------------------------------------
def test_outer_exception_is_error(monkeypatch):
    """EFFECT: a failure in the standings fetch -> status error."""
    client = _FakeFutmondoClient(raises=RuntimeError("standings failed"))
    port = _RecordingPort(last_sync={"last_sync_matchday": 0})
    service = _make_service(monkeypatch, client, port)

    result = service.sync_player_performance()

    assert result["status"] == "error"
    assert "standings failed" in result["error"]
    assert "duration_seconds" in result
    assert port.metadata[0]["sync_status"] == "error"


def test_error_message_carries_no_credentials(monkeypatch):
    """EFFECT (BR4.2): the error payload never leaks the Futmondo password/token."""
    client = _FakeFutmondoClient(raises=RuntimeError("timeout on /matchdayStandings"))
    port = _RecordingPort(last_sync={"last_sync_matchday": 0})
    service = _make_service(monkeypatch, client, port)

    result = service.sync_player_performance()

    assert result["status"] == "error"
    assert "password" not in result["error"].lower()
    assert "token" not in result["error"].lower()


# --- sync_all ordering ----------------------------------------------------
def test_sync_all_keeps_player_performance_key_in_order(monkeypatch):
    """EFFECT (BR3.1): sync_all keeps the ``player_performance`` key in position."""
    port = _RecordingPort()
    service = _make_service(monkeypatch, _FakeFutmondoClient(), port)

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

    assert "player_performance" in results
    assert results["player_performance"] == sentinels["sync_player_performance"]
    keys = list(results.keys())
    assert keys.index("player_performance") == 5
    assert len(keys) == 10
    assert keys[-1] == "prizes"
