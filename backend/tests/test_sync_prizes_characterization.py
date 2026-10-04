"""Characterization tests for ``DataSyncService.sync_prizes`` (uniformised domain).

Freeze the observable behavior across the ``prizes`` uniformisation
(characterization-first, test-after — see the approved Testing Contract). They
assert the EFFECT at the orchestration seam: the early-return statuses
(``no_config`` / ``no_prizes_configured`` / ``no_standings`` / ``no_teams`` /
``no_rounds``), the happy-path ``SyncResult`` payload with its distinctive keys
(``rounds_processed`` / ``records_synced`` / ``stale_prizes_removed``), the atomic
``replace_team_prizes`` call carrying the accumulated rows and valid matchdays,
the typed-exception PROPAGATION (``IntegrationBanError`` fatal; recoverable typed
errors escalate-at-write and propagate), the generic error safety net, no
credential leak, and the ``sync_all`` key position (``prizes``, last). Never
``assert True``.

The pure calculator (``prizes.calculator``) and the atomic writer are reused
UNCHANGED — those are already covered by their own suites
(``test_prizes_characterization``, ``test_prizes_calculator``,
``test_team_prizes_atomic_replacement``); here we characterize the orchestration.

No real DB and no network: deterministic client double + recording port fake.
``time.sleep`` monkeypatched to a no-op. No credentials appear anywhere.
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import pytest  # noqa: E402

import app.services.sync.prizes.orchestrator as orch_mod  # noqa: E402
from app.services.data_sync_service import DataSyncService  # noqa: E402
from app.services.integration_errors import (  # noqa: E402
    IntegrationBanError,
    IntegrationTimeoutError,
)
from app.services.sync.prizes import PrizesSyncOrchestrator  # noqa: E402

CHAMPIONSHIP_ID = "592416daa3a2dd871a7a9956"

# (money_per_ranking, mvp_bonus, ranking_mode, users_to_rank, money_per_point, dream_team_bonus)
_CONFIG_POINTS_ONLY = (0, 0, "flop", -1, 10, 0)


class _RecordingPort:
    def __init__(self, config=None, replace_return=0, replace_raises=None):
        self._config = config
        self._replace_return = replace_return
        self._replace_raises = replace_raises
        self.config_queries = 0
        self.replace_calls = []

    def get_prize_config(self, championship_id):
        self.config_queries += 1
        return self._config

    def replace_team_prizes(self, championship_id, rows, valid_matchdays):
        if self._replace_raises is not None:
            raise self._replace_raises
        self.replace_calls.append(
            {
                "championship_id": championship_id,
                "rows": list(rows),
                "valid_matchdays": set(valid_matchdays),
            }
        )
        return self._replace_return


class _FakeFutmondoClient:
    def __init__(self, standings=None, rounds=None, ranking_by_matchday=None, raises=None):
        self._standings = standings
        self._rounds = rounds or []
        self._ranking_by_matchday = ranking_by_matchday or {}
        self._raises = raises

    def get_matchday_standings(self, championship_id):
        return self._standings

    def get_userteam_rounds(self, championship_id, user_team_id):
        return self._rounds

    def get_round_ranking(self, championship_id, round_number, round_id, userteam_id):
        if self._raises is not None:
            raise self._raises
        return self._ranking_by_matchday.get(round_number)

    def get_round_matches(self, championship_id, round_id, userteam_id):
        return {"matches": []}

    def get_dream_team(self, championship_id, round_id=None):
        return None

    def get_round_lineup(self, championship_id, round_id, team_id):
        return []


def _make_service(monkeypatch, client, port):
    def fake_init(self):
        self.dm = object()
        self.championship_id = CHAMPIONSHIP_ID
        self.league_id = ""
        self.user_id = ""
        self.client = client

    monkeypatch.setattr(DataSyncService, "__init__", fake_init)

    def thin_delegation(self):
        orchestrator = PrizesSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            user_id=self.user_id,
            data=port,
        )
        return orchestrator.sync()

    monkeypatch.setattr(DataSyncService, "sync_prizes", thin_delegation)
    monkeypatch.setattr(orch_mod.time, "sleep", lambda *a, **k: None)
    return DataSyncService()


# --- Early-return short-circuits ------------------------------------------
def test_no_config_returns_no_config(monkeypatch):
    """EFFECT: absent config row -> status no_config, zero records."""
    port = _RecordingPort(config=None)
    service = _make_service(monkeypatch, _FakeFutmondoClient(), port)

    result = service.sync_prizes()

    assert result["status"] == "no_config"
    assert result["records_synced"] == 0
    assert "duration_seconds" in result
    assert port.replace_calls == []


def test_all_prizes_zero_returns_no_prizes_configured(monkeypatch):
    """EFFECT: config present but every prize amount <= 0 -> no_prizes_configured."""
    port = _RecordingPort(config=(0, 0, "flop", -1, 0, 0))
    service = _make_service(monkeypatch, _FakeFutmondoClient(), port)

    result = service.sync_prizes()

    assert result["status"] == "no_prizes_configured"
    assert result["records_synced"] == 0


def test_no_standings_returns_no_standings(monkeypatch):
    """EFFECT: falsy standings -> status no_standings."""
    port = _RecordingPort(config=_CONFIG_POINTS_ONLY)
    client = _FakeFutmondoClient(standings=None)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_prizes()

    assert result["status"] == "no_standings"


def test_no_teams_returns_no_teams(monkeypatch):
    """EFFECT: standings with empty team list -> status no_teams."""
    port = _RecordingPort(config=_CONFIG_POINTS_ONLY)
    client = _FakeFutmondoClient(standings={"teams": []})
    service = _make_service(monkeypatch, client, port)

    result = service.sync_prizes()

    assert result["status"] == "no_teams"


def test_no_rounds_returns_no_rounds(monkeypatch):
    """EFFECT: teams present but no numbered rounds -> status no_rounds."""
    port = _RecordingPort(config=_CONFIG_POINTS_ONLY)
    client = _FakeFutmondoClient(standings={"teams": [{"teamid": "t1"}]}, rounds=[])
    service = _make_service(monkeypatch, client, port)

    result = service.sync_prizes()

    assert result["status"] == "no_rounds"


# --- Happy path -----------------------------------------------------------
def test_points_only_round_persists_atomically(monkeypatch):
    """EFFECT: a points-only round computes rows and replaces atomically; success."""
    port = _RecordingPort(config=_CONFIG_POINTS_ONLY, replace_return=2)
    client = _FakeFutmondoClient(
        standings={"teams": [{"teamid": "t1"}, {"teamid": "t2"}]},
        rounds=[{"id": "r5", "number": 5, "status": "open"}],
        ranking_by_matchday={
            5: {"ranking": [
                {"id": "t1", "points": 30, "position": 1},
                {"id": "t2", "points": 20, "position": 2},
            ]},
        },
    )
    service = _make_service(monkeypatch, client, port)

    result = service.sync_prizes()

    assert result["status"] == "success"
    assert result["rounds_processed"] == 1
    # Two teams -> two computed prize rows accumulated.
    assert result["records_synced"] == 2
    assert result["stale_prizes_removed"] == 2  # whatever the writer returned
    assert isinstance(result["duration_seconds"], float)
    # Atomic replacement called exactly once with the accumulated rows.
    assert len(port.replace_calls) == 1
    call = port.replace_calls[0]
    assert call["championship_id"] == CHAMPIONSHIP_ID
    assert len(call["rows"]) == 2
    assert call["valid_matchdays"] == {5}


def test_no_ranking_data_yields_no_new_data(monkeypatch):
    """EFFECT: a round with no ranking is skipped -> no_new_data when none processed."""
    port = _RecordingPort(config=_CONFIG_POINTS_ONLY)
    client = _FakeFutmondoClient(
        standings={"teams": [{"teamid": "t1"}]},
        rounds=[{"id": "r5", "number": 5, "status": "open"}],
        ranking_by_matchday={},  # no ranking for matchday 5
    )
    service = _make_service(monkeypatch, client, port)

    result = service.sync_prizes()

    assert result["status"] == "no_new_data"
    assert result["rounds_processed"] == 0
    assert result["records_synced"] == 0


# --- Typed-exception propagation ------------------------------------------
def test_integration_ban_error_propagates(monkeypatch):
    """EFFECT (BR2.2/BR3.2): an IntegrationBanError is FATAL and propagates."""
    port = _RecordingPort(config=_CONFIG_POINTS_ONLY)
    client = _FakeFutmondoClient(
        standings={"teams": [{"teamid": "t1"}]},
        rounds=[{"id": "r5", "number": 5, "status": "open"}],
        raises=IntegrationBanError(status=403, endpoint="/ratings"),
    )
    service = _make_service(monkeypatch, client, port)

    with pytest.raises(IntegrationBanError):
        service.sync_prizes()
    # No partial write: the atomic writer was never reached.
    assert port.replace_calls == []


def test_recoverable_integration_error_propagates_at_write(monkeypatch):
    """EFFECT (BR2.3): a recoverable typed error escalates-at-write and propagates."""
    port = _RecordingPort(config=_CONFIG_POINTS_ONLY)
    client = _FakeFutmondoClient(
        standings={"teams": [{"teamid": "t1"}]},
        rounds=[{"id": "r5", "number": 5, "status": "open"}],
        raises=IntegrationTimeoutError(status=504, endpoint="/ranking"),
    )
    service = _make_service(monkeypatch, client, port)

    with pytest.raises(IntegrationTimeoutError):
        service.sync_prizes()
    assert port.replace_calls == []


def test_writer_failure_propagates_as_fatal(monkeypatch):
    """EFFECT (NFR2): a failure in the atomic writer surfaces (never swallowed).

    The generic safety net turns a non-typed write failure into a status error
    rather than leaving a mixed state.
    """
    port = _RecordingPort(
        config=_CONFIG_POINTS_ONLY, replace_raises=RuntimeError("txn rolled back")
    )
    client = _FakeFutmondoClient(
        standings={"teams": [{"teamid": "t1"}]},
        rounds=[{"id": "r5", "number": 5, "status": "open"}],
        ranking_by_matchday={5: {"ranking": [{"id": "t1", "points": 10, "position": 1}]}},
    )
    service = _make_service(monkeypatch, client, port)

    result = service.sync_prizes()

    assert result["status"] == "error"
    assert "txn rolled back" in result["error"]
    assert result["records_synced"] == 0


def test_error_message_carries_no_credentials(monkeypatch):
    """EFFECT (BR4.2): the generic error payload never leaks the password/token."""
    port = _RecordingPort(
        config=_CONFIG_POINTS_ONLY, replace_raises=RuntimeError("timeout on /ranking")
    )
    client = _FakeFutmondoClient(
        standings={"teams": [{"teamid": "t1"}]},
        rounds=[{"id": "r5", "number": 5, "status": "open"}],
        ranking_by_matchday={5: {"ranking": [{"id": "t1", "points": 10, "position": 1}]}},
    )
    service = _make_service(monkeypatch, client, port)

    result = service.sync_prizes()

    assert result["status"] == "error"
    assert "password" not in result["error"].lower()
    assert "token" not in result["error"].lower()


# --- sync_all ordering ----------------------------------------------------
def test_sync_all_keeps_prizes_key_last(monkeypatch):
    """EFFECT (BR3.1): sync_all keeps the literal ``prizes`` key last."""
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

    assert "prizes" in results
    assert results["prizes"] == sentinels["sync_prizes"]
    keys = list(results.keys())
    assert keys[-1] == "prizes"
    assert keys.index("prizes") == 9
    assert len(keys) == 10
