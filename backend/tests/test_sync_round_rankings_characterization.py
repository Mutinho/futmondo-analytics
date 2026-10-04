"""Characterization tests for ``DataSyncService.sync_round_rankings``.

Freeze the observable behavior across the ``round_rankings`` extraction
(characterization-first, test-after — see the approved Testing Contract). They
assert the EFFECT: the observable ``SyncResult`` payload with its distinctive
keys (status, ``rounds_synced``, ``records_synced``, ``last_matchday``,
``duration_seconds``), the per-matchday ingestion from matchday 1, the
``save_round_ranking`` argument order ``(matchday, championship_id, teams)``, the
consecutive-miss stop (>= 2), the per-matchday break-on-error, the ``no_new_data``
when nothing synced, the outer failure mode, no credential leak, the
``team_standings`` data type, and the ``sync_all`` key position
(``team_standings``). Never ``assert True``.

No real DB and no network: deterministic client double + recording port fake.
``time.sleep`` monkeypatched to a no-op. No credentials appear anywhere.
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import app.services.sync.round_rankings.orchestrator as orch_mod  # noqa: E402
from app.services.data_sync_service import DataSyncService  # noqa: E402
from app.services.sync.round_rankings import RoundRankingsSyncOrchestrator  # noqa: E402

CHAMPIONSHIP_ID = "592416daa3a2dd871a7a9956"


class _RecordingPort:
    def __init__(self, latest_matchday=0):
        self._latest = latest_matchday
        self.saved = []
        self.metadata = []

    def save_round_ranking(self, matchday, championship_id, teams):
        self.saved.append(
            {"matchday": matchday, "championship_id": championship_id, "teams": list(teams)}
        )

    def get_latest_matchday(self, championship_id):
        return self._latest

    def update_sync_metadata(self, **kwargs):
        self.metadata.append(kwargs)


class _FakeFutmondoClient:
    """Deterministic double for the client calls round-rankings sync uses."""

    def __init__(self, standings=None, user_rounds=None, rankings=None, raises=None):
        self._standings = standings
        self._user_rounds = user_rounds or []
        self._rankings = rankings or {}
        self._raises = raises

    def get_matchday_standings(self, championship_id):
        if self._raises is not None:
            raise self._raises
        return self._standings

    def get_userteam_rounds(self, championship_id, team_id):
        return self._user_rounds

    def get_round_ranking(self, championship_id, round_number, round_id, userteam_id):
        return self._rankings.get(round_number)


def _make_service(monkeypatch, client, port):
    def fake_init(self):
        self.dm = object()
        self.championship_id = CHAMPIONSHIP_ID
        self.league_id = ""
        self.user_id = ""
        self.client = client

    monkeypatch.setattr(DataSyncService, "__init__", fake_init)

    def thin_delegation(self):
        orchestrator = RoundRankingsSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            data=port,
        )
        return orchestrator.sync()

    monkeypatch.setattr(DataSyncService, "sync_round_rankings", thin_delegation)
    monkeypatch.setattr(orch_mod.time, "sleep", lambda *a, **k: None)
    return DataSyncService()


# --- Happy path -----------------------------------------------------------
def test_success_syncs_matchdays_until_consecutive_misses(monkeypatch):
    """EFFECT: matchdays 1-2 have data, 3-4 empty -> stop after 2 misses; success."""
    client = _FakeFutmondoClient(
        standings={"teams": [{"id": "ut1"}]},
        user_rounds=[
            {"id": "r1", "number": 1},
            {"id": "r2", "number": 2},
        ],
        rankings={
            1: {"teams": [{"id": "t1"}, {"id": "t2"}]},
            2: {"ranking": [{"id": "t1"}]},
            # 3 and 4 missing -> empty -> 2 consecutive misses -> stop
        },
    )
    port = _RecordingPort(latest_matchday=2)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_round_rankings()

    assert result["status"] == "success"
    assert result["rounds_synced"] == 2
    assert result["records_synced"] == 3  # 2 + 1 teams
    assert result["last_matchday"] == 2  # from get_latest_matchday
    assert isinstance(result["duration_seconds"], float)
    # save_round_ranking called with the historical arg order.
    assert port.saved[0]["matchday"] == 1
    assert port.saved[0]["championship_id"] == CHAMPIONSHIP_ID
    assert [t["id"] for t in port.saved[0]["teams"]] == ["t1", "t2"]
    assert port.metadata[0]["sync_status"] == "success"
    assert port.metadata[0]["data_type"] == "team_standings"
    assert port.metadata[0]["last_sync_matchday"] == 2


def test_no_rankings_anywhere_is_no_new_data(monkeypatch):
    """EFFECT: every matchday empty -> no rounds synced -> no_new_data."""
    client = _FakeFutmondoClient(
        standings={"teams": [{"id": "ut1"}]},
        user_rounds=[{"id": "r1", "number": 1}],
        rankings={},
    )
    port = _RecordingPort(latest_matchday=0)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_round_rankings()

    assert result["status"] == "no_new_data"
    assert result["rounds_synced"] == 0
    assert result["records_synced"] == 0
    assert port.saved == []
    assert port.metadata[0]["sync_status"] == "no_new_data"


def test_ranking_as_bare_list_is_accepted(monkeypatch):
    """EFFECT: a round ranking returned as a bare list is persisted."""
    client = _FakeFutmondoClient(
        standings={"teams": [{"id": "ut1"}]},
        user_rounds=[{"id": "r1", "number": 1}],
        rankings={1: [{"id": "t1"}, {"id": "t2"}, {"id": "t3"}]},
    )
    port = _RecordingPort(latest_matchday=1)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_round_rankings()

    assert result["status"] == "success"
    assert result["rounds_synced"] == 1
    assert result["records_synced"] == 3


def test_per_matchday_exception_breaks_the_loop(monkeypatch):
    """EFFECT: an exception while fetching a ranking breaks (not raise)."""

    class _FailingClient(_FakeFutmondoClient):
        def get_round_ranking(self, championship_id, round_number, round_id, userteam_id):
            raise RuntimeError("ranking fetch failed")

    client = _FailingClient(
        standings={"teams": [{"id": "ut1"}]},
        user_rounds=[{"id": "r1", "number": 1}],
    )
    port = _RecordingPort(latest_matchday=0)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_round_rankings()

    # The loop broke on the first matchday; nothing synced -> no_new_data.
    assert result["status"] == "no_new_data"
    assert result["rounds_synced"] == 0
    assert port.saved == []


# --- Failure modes --------------------------------------------------------
def test_outer_exception_is_error(monkeypatch):
    """EFFECT: a failure in the standings fetch -> status error."""
    client = _FakeFutmondoClient(raises=RuntimeError("standings failed"))
    port = _RecordingPort(latest_matchday=0)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_round_rankings()

    assert result["status"] == "error"
    assert "standings failed" in result["error"]
    assert "duration_seconds" in result
    assert port.metadata[0]["sync_status"] == "error"


def test_error_message_carries_no_credentials(monkeypatch):
    """EFFECT (BR4.2): the error payload never leaks the Futmondo password/token."""
    client = _FakeFutmondoClient(raises=RuntimeError("timeout on /matchdayStandings"))
    port = _RecordingPort(latest_matchday=0)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_round_rankings()

    assert result["status"] == "error"
    assert "password" not in result["error"].lower()
    assert "token" not in result["error"].lower()


# --- sync_all ordering ----------------------------------------------------
def test_sync_all_keeps_team_standings_key_in_order(monkeypatch):
    """EFFECT (BR3.1): sync_all routes sync_round_rankings under ``team_standings``."""
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

    # The round-rankings result is routed under the ``team_standings`` key (divergence).
    assert "team_standings" in results
    assert results["team_standings"] == sentinels["sync_round_rankings"]
    keys = list(results.keys())
    assert keys.index("team_standings") == 7
    assert len(keys) == 10
    assert keys[-1] == "prizes"
