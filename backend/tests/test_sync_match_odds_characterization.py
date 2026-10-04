"""Characterization tests for ``DataSyncService.sync_match_odds`` (safety net).

These freeze the CURRENT observable behavior of ``sync_match_odds`` BEFORE the
``match_odds`` domain is extracted (characterization-first, test-after — see the
approved Testing Contract). They assert the EFFECT: the observable ``SyncResult``
payload (status, keys, ``records_synced``, ``matchday``, ``duration_seconds``),
the recoverable-vs-fatal failure mode, and that ``sync_all`` keeps the literal
``match_odds`` key in its result at the historical position. Never ``assert True``.

The SAME tests run green against the extracted code (equivalence, FR5).

No real DB and no network: the Futmondo API client is a deterministic double and
``self.dm`` is a recording fake capturing the two persistence calls
``sync_match_odds`` makes (``save_match_odds`` + ``update_sync_metadata``).
``time.sleep`` is monkeypatched to a no-op. No credentials appear anywhere.
"""

import os

# ``app.core.config`` hardens JWT startup (NFR1.1): set a non-default secret
# BEFORE importing the app so instantiating the service does not fail at import.
os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import app.services.data_sync_service as dss  # noqa: E402,F401
import app.services.sync.match_odds.orchestrator as match_odds_orch  # noqa: E402
from app.services.data_sync_service import DataSyncService  # noqa: E402

CHAMPIONSHIP_ID = "592416daa3a2dd871a7a9956"


class _RecordingDM:
    """Records the two persistence calls ``sync_match_odds`` makes (no DB)."""

    def __init__(self):
        self.saved = []
        self.metadata = []

    def save_match_odds(self, championship_id, matches, round_id=None, matchday=None):
        self.saved.append(
            {
                "championship_id": championship_id,
                "matches": matches,
                "round_id": round_id,
                "matchday": matchday,
            }
        )

    def update_sync_metadata(self, **kwargs):
        self.metadata.append(kwargs)


class _FakeFutmondoClient:
    """Deterministic double: only ``get_match_list`` is used by match_odds sync."""

    def __init__(self, match_list=None, raises=None):
        self._match_list = match_list
        self._raises = raises

    def get_match_list(self, championship_id, matchday=None):
        if self._raises is not None:
            raise self._raises
        return self._match_list


def _make_service(monkeypatch, client, dm):
    """Build a ``DataSyncService`` with fakes, avoiding real DB/network init."""

    def fake_init(self):
        self.dm = dm
        self.championship_id = CHAMPIONSHIP_ID
        self.league_id = ""
        self.user_id = ""
        self.client = client

    monkeypatch.setattr(DataSyncService, "__init__", fake_init)
    monkeypatch.setattr(match_odds_orch.time, "sleep", lambda *a, **k: None)
    return DataSyncService()


# --- Happy path -----------------------------------------------------------
def test_success_returns_frozen_payload_and_persists(monkeypatch):
    """EFFECT: two matches -> status success, records_synced=2, matchday echoed."""
    client = _FakeFutmondoClient(
        match_list={
            "round": {"_id": "r7", "number": 7},
            "matches": [{"_id": "m1"}, {"_id": "m2"}],
        }
    )
    dm = _RecordingDM()
    service = _make_service(monkeypatch, client, dm)

    result = service.sync_match_odds()

    assert result["status"] == "success"
    assert result["records_synced"] == 2
    assert result["matchday"] == 7
    assert "duration_seconds" in result
    assert isinstance(result["duration_seconds"], float)
    # Persistence delegated verbatim: odds saved with round_id/matchday.
    assert len(dm.saved) == 1
    assert dm.saved[0]["round_id"] == "r7"
    assert dm.saved[0]["matchday"] == 7
    assert len(dm.saved[0]["matches"]) == 2
    # Sync metadata recorded with the success status and count.
    assert len(dm.metadata) == 1
    assert dm.metadata[0]["sync_status"] == "success"
    assert dm.metadata[0]["records_synced"] == 2
    assert dm.metadata[0]["data_type"] == "match_odds"


def test_empty_matches_still_success_with_zero_records(monkeypatch):
    """EFFECT: an empty match list still succeeds with records_synced=0."""
    client = _FakeFutmondoClient(
        match_list={"round": {"_id": "r8", "number": 8}, "matches": []}
    )
    dm = _RecordingDM()
    service = _make_service(monkeypatch, client, dm)

    result = service.sync_match_odds()

    assert result["status"] == "success"
    assert result["records_synced"] == 0
    assert result["matchday"] == 8
    assert "duration_seconds" in result


def test_missing_round_number_yields_none_matchday(monkeypatch):
    """EFFECT: absent round.number -> matchday is None, still success."""
    client = _FakeFutmondoClient(match_list={"round": {}, "matches": [{"_id": "m1"}]})
    dm = _RecordingDM()
    service = _make_service(monkeypatch, client, dm)

    result = service.sync_match_odds()

    assert result["status"] == "success"
    assert result["matchday"] is None
    assert result["records_synced"] == 1


# --- Failure modes --------------------------------------------------------
def test_empty_api_response_is_error(monkeypatch):
    """EFFECT: a falsy API response -> status error, error message present."""
    client = _FakeFutmondoClient(match_list=None)
    dm = _RecordingDM()
    service = _make_service(monkeypatch, client, dm)

    result = service.sync_match_odds()

    assert result["status"] == "error"
    assert "error" in result
    assert "duration_seconds" in result
    # No odds were saved on the error path; metadata records the error status.
    assert dm.saved == []
    assert len(dm.metadata) == 1
    assert dm.metadata[0]["sync_status"] == "error"


def test_client_exception_is_caught_as_error(monkeypatch):
    """EFFECT: an ingestion exception is caught -> status error (not raised)."""
    client = _FakeFutmondoClient(raises=RuntimeError("upstream failed"))
    dm = _RecordingDM()
    service = _make_service(monkeypatch, client, dm)

    result = service.sync_match_odds()

    assert result["status"] == "error"
    assert "upstream failed" in result["error"]
    assert dm.saved == []


def test_error_message_carries_no_credentials(monkeypatch):
    """EFFECT (BR4.2): the error payload never leaks the Futmondo password/token."""
    client = _FakeFutmondoClient(raises=RuntimeError("timeout on /matchList"))
    dm = _RecordingDM()
    service = _make_service(monkeypatch, client, dm)

    result = service.sync_match_odds()

    assert result["status"] == "error"
    assert "password" not in result["error"].lower()
    assert "token" not in result["error"].lower()


# --- sync_all ordering ----------------------------------------------------
def test_sync_all_keeps_match_odds_key_in_order(monkeypatch):
    """EFFECT (BR3.1): sync_all keeps the literal ``match_odds`` key in position.

    Every ``sync_*`` is stubbed to a sentinel so ``sync_all`` runs without DB or
    network; the assertion is on the presence, value routing, and ORDER of the
    ``match_odds`` key in the aggregate result.
    """
    dm = _RecordingDM()
    service = _make_service(monkeypatch, _FakeFutmondoClient(), dm)

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

    assert "match_odds" in results
    assert results["match_odds"] == sentinels["sync_match_odds"]
    # Historical key order is preserved (match_odds is the 9th key, before prizes).
    keys = list(results.keys())
    assert keys.index("match_odds") == 8
    assert keys[-1] == "prizes"
