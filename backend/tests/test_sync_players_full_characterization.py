"""Characterization tests for ``DataSyncService.sync_players_full``.

Freeze the observable behavior across the ``players_full`` extraction
(characterization-first, test-after — see the approved Testing Contract). They
assert the EFFECT: the observable ``SyncResult`` payload (status, keys,
``records_synced``, ``duration_seconds``), the record/stats payload assembly, the
batch upsert count surfaced as ``records_synced``, the orphan cleanup call, the
stats persistence, the favorites selection (fav True AND no userteamId) with the
``user_id`` resolved from the client, the non-critical sub-step isolation
(orphan/stats/favorites failures do not fail the sync), the fatal empty-players
error, no credential leak, the ``players`` data type, and the ``sync_all``
name-key divergence (``players`` <- sync_players_full). Never ``assert True``.

No real DB and no network: deterministic client double + recording port fake.
``time.sleep`` monkeypatched to a no-op. No credentials appear anywhere.
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import app.services.sync.players_full.orchestrator as orch_mod  # noqa: E402
from app.services.data_sync_service import DataSyncService  # noqa: E402
from app.services.sync.players_full import PlayersFullSyncOrchestrator  # noqa: E402

CHAMPIONSHIP_ID = "592416daa3a2dd871a7a9956"


class _RecordingPort:
    def __init__(self, batch_count=0, orphans=0, raises=None):
        self._batch_count = batch_count
        self._orphans = orphans
        self._raises = raises or {}
        self.players_batches = []
        self.orphan_calls = []
        self.stats_calls = []
        self.favorites_calls = []
        self.metadata = []

    def save_players_batch(self, player_records):
        self.players_batches.append(list(player_records))
        return self._batch_count

    def delete_orphan_players(self, live_ids):
        if "orphans" in self._raises:
            raise self._raises["orphans"]
        self.orphan_calls.append(list(live_ids))
        return self._orphans

    def save_player_championship_stats(self, championship_id, stats_payload):
        if "stats" in self._raises:
            raise self._raises["stats"]
        self.stats_calls.append({"championship_id": championship_id, "stats": list(stats_payload)})

    def save_favorites(self, championship_id, user_id, player_ids):
        if "favorites" in self._raises:
            raise self._raises["favorites"]
        self.favorites_calls.append(
            {"championship_id": championship_id, "user_id": user_id, "player_ids": list(player_ids)}
        )

    def update_sync_metadata(self, **kwargs):
        self.metadata.append(kwargs)


class _FakeFutmondoClient:
    def __init__(self, players_data=None, raises=None, user_id="user-42"):
        self._players_data = players_data
        self._raises = raises
        self.user_id = user_id

    def get_championship_players(self, championship_id):
        if self._raises is not None:
            raise self._raises
        return self._players_data


def _make_service(monkeypatch, client, port):
    def fake_init(self):
        self.dm = object()
        self.championship_id = CHAMPIONSHIP_ID
        self.league_id = ""
        self.user_id = ""
        self.client = client

    monkeypatch.setattr(DataSyncService, "__init__", fake_init)

    def thin_delegation(self):
        orchestrator = PlayersFullSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            data=port,
        )
        return orchestrator.sync()

    monkeypatch.setattr(DataSyncService, "sync_players_full", thin_delegation)
    monkeypatch.setattr(orch_mod.time, "sleep", lambda *a, **k: None)
    return DataSyncService()


# --- Happy path -----------------------------------------------------------
def test_success_persists_records_stats_and_favorites(monkeypatch):
    """EFFECT: records batched, stats saved, favorites selected; success."""
    players = [
        {"id": "p1", "name": "A", "fav": True},  # fav + no userteamId -> favorite
        {"id": "p2", "name": "B", "userteamId": "ut9", "fav": True},  # owned -> NOT fav
        {"id": "p3", "name": "C"},
    ]
    client = _FakeFutmondoClient(players_data={"players": players}, user_id="user-42")
    port = _RecordingPort(batch_count=3, orphans=1)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_players_full()

    assert result["status"] == "success"
    # records_synced is whatever save_players_batch returned.
    assert result["records_synced"] == 3
    assert isinstance(result["duration_seconds"], float)
    assert len(port.players_batches) == 1
    assert [r["id"] for r in port.players_batches[0]] == ["p1", "p2", "p3"]
    # Orphan cleanup called with the live ids.
    assert port.orphan_calls == [["p1", "p2", "p3"]]
    # Stats persisted for all players.
    assert len(port.stats_calls) == 1
    assert len(port.stats_calls[0]["stats"]) == 3
    # Favorites: only p1 (fav True AND no userteamId); user_id resolved from client.
    assert len(port.favorites_calls) == 1
    assert port.favorites_calls[0]["player_ids"] == ["p1"]
    assert port.favorites_calls[0]["user_id"] == "user-42"
    assert port.metadata[0]["sync_status"] == "success"
    assert port.metadata[0]["data_type"] == "players"
    assert port.metadata[0]["records_synced"] == 3


def test_favorites_user_id_falls_back_to_empty_string(monkeypatch):
    """EFFECT: a falsy client.user_id resolves to '' for favorites (historical)."""
    players = [{"id": "p1", "fav": True}]
    client = _FakeFutmondoClient(players_data={"players": players}, user_id=None)
    port = _RecordingPort(batch_count=1)
    service = _make_service(monkeypatch, client, port)

    service.sync_players_full()

    assert port.favorites_calls[0]["user_id"] == ""


def test_noncritical_substep_failures_do_not_fail_sync(monkeypatch):
    """EFFECT: orphan/stats/favorites failures are swallowed; sync still succeeds."""
    players = [{"id": "p1", "fav": True}]
    client = _FakeFutmondoClient(players_data={"players": players})
    port = _RecordingPort(
        batch_count=1,
        raises={
            "orphans": RuntimeError("orphan cleanup boom"),
            "stats": RuntimeError("stats boom"),
            "favorites": RuntimeError("favorites boom"),
        },
    )
    service = _make_service(monkeypatch, client, port)

    result = service.sync_players_full()

    assert result["status"] == "success"
    assert result["records_synced"] == 1
    assert port.metadata[0]["sync_status"] == "success"


# --- Failure modes --------------------------------------------------------
def test_empty_players_is_fatal_error(monkeypatch):
    """EFFECT: no players returned -> raised and caught as status error."""
    client = _FakeFutmondoClient(players_data={"players": []})
    port = _RecordingPort()
    service = _make_service(monkeypatch, client, port)

    result = service.sync_players_full()

    assert result["status"] == "error"
    assert "Could not fetch championship players" in result["error"]
    assert "duration_seconds" in result
    assert port.players_batches == []
    assert port.metadata[0]["sync_status"] == "error"


def test_client_exception_is_error(monkeypatch):
    """EFFECT: an ingestion exception -> status error."""
    client = _FakeFutmondoClient(raises=RuntimeError("players fetch failed"))
    port = _RecordingPort()
    service = _make_service(monkeypatch, client, port)

    result = service.sync_players_full()

    assert result["status"] == "error"
    assert "players fetch failed" in result["error"]


def test_error_message_carries_no_credentials(monkeypatch):
    """EFFECT (BR4.2): the error payload never leaks the Futmondo password/token."""
    client = _FakeFutmondoClient(raises=RuntimeError("timeout on /championshipPlayers"))
    port = _RecordingPort()
    service = _make_service(monkeypatch, client, port)

    result = service.sync_players_full()

    assert result["status"] == "error"
    assert "password" not in result["error"].lower()
    assert "token" not in result["error"].lower()


# --- sync_all ordering ----------------------------------------------------
def test_sync_all_routes_under_players_key_first(monkeypatch):
    """EFFECT (BR3.1): sync_all routes sync_players_full under the ``players`` key."""
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

    # Name-key divergence: players <- sync_players_full, and it is the FIRST key.
    assert "players" in results
    assert results["players"] == sentinels["sync_players_full"]
    keys = list(results.keys())
    assert keys.index("players") == 0
    assert len(keys) == 10
    assert keys[-1] == "prizes"
