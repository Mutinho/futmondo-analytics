"""Characterization tests for ``DataSyncService.sync_punishments_bonuses``.

Freeze the observable behavior across the ``punishments_bonuses`` extraction
(characterization-first, test-after — see the approved Testing Contract). They
assert the EFFECT: the observable ``SyncResult`` payload (status, keys,
``records_synced``, ``last_sync_id``, ``duration_seconds``), the ``styp in
['punish','bonus']`` filtering, de-duplication, the "no new items -> stop"
condition, the ``success if total_synced > 0 or from_id else no_new_data`` status
rule, the outer failure mode, no credential leak, and the ``sync_all`` key
position. Never ``assert True``.

No real DB and no network: deterministic client double + recording port fake.
``time.sleep`` is monkeypatched to a no-op. No credentials appear anywhere.
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import app.services.sync.punishments_bonuses.orchestrator as orch_mod  # noqa: E402
from app.services.data_sync_service import DataSyncService  # noqa: E402

CHAMPIONSHIP_ID = "592416daa3a2dd871a7a9956"


class _RecordingPort:
    def __init__(self, last_sync=None):
        self._last_sync = last_sync
        self.last_sync_queries = []
        self.saved = []
        self.metadata = []

    def get_last_sync_metadata(self, championship_id, data_type):
        self.last_sync_queries.append(
            {"championship_id": championship_id, "data_type": data_type}
        )
        return self._last_sync

    def save_punishments_bonuses(self, championship_id, items):
        self.saved.append({"championship_id": championship_id, "items": list(items)})

    def update_sync_metadata(self, **kwargs):
        self.metadata.append(kwargs)


class _FakeFutmondoClient:
    """Deterministic double: only ``get_locker_news`` is used."""

    def __init__(self, pages=None, raises=None):
        self._pages = list(pages or [])
        self._raises = raises
        self.calls = []

    def get_locker_news(self, championship_id, from_id=None):
        self.calls.append({"championship_id": championship_id, "from_id": from_id})
        if self._raises is not None:
            raise self._raises
        if self._pages:
            return self._pages.pop(0)
        return {}


def _make_service(monkeypatch, client, port):
    def fake_init(self):
        self.dm = object()
        self.championship_id = CHAMPIONSHIP_ID
        self.league_id = ""
        self.user_id = ""
        self.client = client

    monkeypatch.setattr(DataSyncService, "__init__", fake_init)

    def thin_delegation(self):
        from app.services.sync.punishments_bonuses import (
            PunishmentsBonusesSyncOrchestrator,
        )

        orchestrator = PunishmentsBonusesSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            data=port,
        )
        return orchestrator.sync()

    monkeypatch.setattr(DataSyncService, "sync_punishments_bonuses", thin_delegation)
    monkeypatch.setattr(orch_mod.time, "sleep", lambda *a, **k: None)
    return DataSyncService()


# --- Happy path -----------------------------------------------------------
def test_success_filters_and_persists(monkeypatch):
    """EFFECT: punish/bonus items persisted, others filtered; success + last id."""
    client = _FakeFutmondoClient(
        pages=[
            {
                "news": [
                    {"_id": "pb1", "styp": "punish"},
                    {"_id": "c1", "styp": "clause"},  # filtered out
                    {"_id": "pb2", "styp": "bonus"},
                ]
            },
            # Second page: trailing item id drives from_id; no new punish/bonus
            # items -> stop. The trailing item of page 1 is pb2.
            {"news": [{"_id": "c2", "styp": "clause"}]},
        ]
    )
    port = _RecordingPort(last_sync=None)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_punishments_bonuses()

    assert result["status"] == "success"
    assert result["records_synced"] == 2
    # last_news_id is the trailing item of the LAST page that saved items (pb2).
    assert result["last_sync_id"] == "pb2"
    assert isinstance(result["duration_seconds"], float)
    assert len(port.saved) == 1
    saved_ids = [i["_id"] for i in port.saved[0]["items"]]
    assert saved_ids == ["pb1", "pb2"]
    assert port.metadata[0]["sync_status"] == "success"
    assert port.metadata[0]["data_type"] == "punishments_bonuses"
    assert port.metadata[0]["records_synced"] == 2


def test_no_items_first_page_is_no_new_data(monkeypatch):
    """EFFECT: no punish/bonus and no prior from_id -> no_new_data."""
    client = _FakeFutmondoClient(pages=[{"news": [{"_id": "c1", "styp": "clause"}]}])
    port = _RecordingPort(last_sync=None)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_punishments_bonuses()

    assert result["status"] == "no_new_data"
    assert result["records_synced"] == 0
    assert result["last_sync_id"] == ""
    assert port.saved == []
    assert port.metadata[0]["sync_status"] == "no_new_data"


def test_prior_from_id_makes_empty_run_success(monkeypatch):
    """EFFECT: with a prior last_sync_id and no new items, status is success.

    The ``or from_id`` branch keeps the historical quirk: an incremental run
    starting from a known id reports ``success`` even with zero new records.
    """
    client = _FakeFutmondoClient(pages=[{"news": [{"_id": "c1", "styp": "clause"}]}])
    port = _RecordingPort(last_sync={"last_sync_id": "prev-id"})
    service = _make_service(monkeypatch, client, port)

    result = service.sync_punishments_bonuses()

    assert result["status"] == "success"
    assert result["records_synced"] == 0
    assert result["last_sync_id"] == "prev-id"


def test_dedup_within_page(monkeypatch):
    """EFFECT: a repeated id within the page is persisted once."""
    client = _FakeFutmondoClient(
        pages=[
            {
                "news": [
                    {"_id": "pb1", "styp": "bonus"},
                    {"_id": "pb1", "styp": "bonus"},
                    {"_id": "pb2", "styp": "punish"},
                ]
            },
            {"news": []},
        ]
    )
    port = _RecordingPort(last_sync=None)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_punishments_bonuses()

    assert result["records_synced"] == 2
    saved_ids = [i["_id"] for i in port.saved[0]["items"]]
    assert saved_ids == ["pb1", "pb2"]


# --- Failure modes --------------------------------------------------------
def test_client_exception_is_error(monkeypatch):
    """EFFECT: an ingestion exception -> status error (caught by outer except)."""
    client = _FakeFutmondoClient(raises=RuntimeError("locker fetch failed"))
    port = _RecordingPort(last_sync=None)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_punishments_bonuses()

    assert result["status"] == "error"
    assert "locker fetch failed" in result["error"]
    assert "duration_seconds" in result
    assert port.saved == []
    assert port.metadata[0]["sync_status"] == "error"


def test_error_message_carries_no_credentials(monkeypatch):
    """EFFECT (BR4.2): the error payload never leaks the Futmondo password/token."""
    client = _FakeFutmondoClient(raises=RuntimeError("timeout on /lockerNews"))
    port = _RecordingPort(last_sync=None)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_punishments_bonuses()

    assert result["status"] == "error"
    assert "password" not in result["error"].lower()
    assert "token" not in result["error"].lower()


# --- sync_all ordering ----------------------------------------------------
def test_sync_all_keeps_punishments_key_in_order(monkeypatch):
    """EFFECT (BR3.1): sync_all keeps the ``punishments_bonuses`` key in position."""
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

    assert "punishments_bonuses" in results
    assert results["punishments_bonuses"] == sentinels["sync_punishments_bonuses"]
    keys = list(results.keys())
    assert keys.index("punishments_bonuses") == 3
    assert len(keys) == 10
    assert keys[-1] == "prizes"
