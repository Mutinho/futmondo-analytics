"""Characterization tests for ``DataSyncService.sync_clauses`` (safety net).

These freeze the CURRENT observable behavior of ``sync_clauses`` BEFORE the
``clauses`` domain is extracted (characterization-first, test-after — see the
approved Testing Contract). They assert the EFFECT: the observable ``SyncResult``
payload (status, keys, ``records_synced``, ``last_sync_id``,
``duration_seconds``), the paginated ingestion and ``styp == 'clause'``
filtering, the de-duplication, the previously-synced-id stop condition, the
recoverable per-page failure (log-and-break, not raise), the outer failure mode,
and that ``sync_all`` keeps the literal ``clauses`` key in its historical
position. Never ``assert True``.

The SAME tests run green against the extracted code (equivalence, FR5).

No real DB and no network: the Futmondo API client is a deterministic double and
``self.dm`` is a recording fake capturing the three persistence calls
``sync_clauses`` makes (``get_last_sync_metadata`` + ``save_clauses`` +
``update_sync_metadata``). ``time.sleep`` is monkeypatched to a no-op. No
credentials appear anywhere.
"""

import os

# ``app.core.config`` hardens JWT startup (NFR1.1): set a non-default secret
# BEFORE importing the app so instantiating the service does not fail at import.
os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import app.services.data_sync_service as dss  # noqa: E402,F401
import app.services.sync.clauses.orchestrator as clauses_orch  # noqa: E402
from app.services.data_sync_service import DataSyncService  # noqa: E402

CHAMPIONSHIP_ID = "592416daa3a2dd871a7a9956"


class _RecordingDM:
    """Records the three persistence calls ``sync_clauses`` makes (no DB)."""

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

    def save_clauses(self, championship_id, news_items):
        self.saved.append(
            {"championship_id": championship_id, "news_items": list(news_items)}
        )

    def update_sync_metadata(self, **kwargs):
        self.metadata.append(kwargs)


class _FakeFutmondoClient:
    """Deterministic double: only ``get_locker_news`` is used by clauses sync.

    ``pages`` is a list of locker-news payloads returned in order; after the
    list is exhausted an empty dict is returned (so pagination terminates).
    ``raises`` (if set) is raised on the first call to simulate an ingestion
    failure inside the per-page try/except.
    """

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


def _make_service(monkeypatch, client, dm):
    """Build a ``DataSyncService`` with fakes, avoiding real DB/network init."""

    def fake_init(self):
        self.dm = dm
        self.championship_id = CHAMPIONSHIP_ID
        self.league_id = ""
        self.user_id = ""
        self.client = client

    monkeypatch.setattr(DataSyncService, "__init__", fake_init)
    monkeypatch.setattr(clauses_orch.time, "sleep", lambda *a, **k: None)
    return DataSyncService()


# --- Happy path -----------------------------------------------------------
def test_success_returns_frozen_payload_and_persists(monkeypatch):
    """EFFECT: two clause items -> status success, records_synced=2, newest id echoed."""
    client = _FakeFutmondoClient(
        pages=[
            {
                "news": [
                    {"_id": "c1", "styp": "clause"},
                    {"_id": "x1", "styp": "transfer"},
                    {"_id": "c2", "styp": "clause"},
                ]
            }
        ]
    )
    dm = _RecordingDM(last_sync=None)
    service = _make_service(monkeypatch, client, dm)

    result = service.sync_clauses()

    assert result["status"] == "success"
    assert result["records_synced"] == 2
    # newest_news_id is the FIRST clause encountered (c1).
    assert result["last_sync_id"] == "c1"
    assert "duration_seconds" in result
    assert isinstance(result["duration_seconds"], float)
    # Only the two clause items are persisted (transfer filtered out).
    assert len(dm.saved) == 1
    saved_ids = [item["_id"] for item in dm.saved[0]["news_items"]]
    assert saved_ids == ["c1", "c2"]
    # The last-sync lookup was performed with the clauses data type.
    assert dm.last_sync_queries == [
        {"championship_id": CHAMPIONSHIP_ID, "data_type": "clauses"}
    ]
    # Sync metadata recorded success with count and newest id.
    assert len(dm.metadata) == 1
    assert dm.metadata[0]["sync_status"] == "success"
    assert dm.metadata[0]["records_synced"] == 2
    assert dm.metadata[0]["data_type"] == "clauses"
    assert dm.metadata[0]["last_sync_id"] == "c1"


def test_no_clauses_yields_no_new_data(monkeypatch):
    """EFFECT: a page with no clause items -> status no_new_data, zero records."""
    client = _FakeFutmondoClient(
        pages=[{"news": [{"_id": "x1", "styp": "transfer"}]}]
    )
    dm = _RecordingDM(last_sync=None)
    service = _make_service(monkeypatch, client, dm)

    result = service.sync_clauses()

    assert result["status"] == "no_new_data"
    assert result["records_synced"] == 0
    # No new clauses and no previous id -> last_sync_id falls back to "".
    assert result["last_sync_id"] == ""
    assert dm.saved == []
    assert len(dm.metadata) == 1
    assert dm.metadata[0]["sync_status"] == "no_new_data"
    assert dm.metadata[0]["records_synced"] == 0


def test_dedup_across_pages(monkeypatch):
    """EFFECT: a repeated clause ``_id`` across pages is persisted only once."""
    client = _FakeFutmondoClient(
        pages=[
            {"news": [{"_id": "c1", "styp": "clause"}, {"_id": "p1", "styp": "x"}]},
            {"news": [{"_id": "c1", "styp": "clause"}, {"_id": "c2", "styp": "clause"}]},
        ]
    )
    dm = _RecordingDM(last_sync=None)
    service = _make_service(monkeypatch, client, dm)

    result = service.sync_clauses()

    assert result["status"] == "success"
    # c1 appears on both pages but is deduped -> total 2 (c1, c2).
    assert result["records_synced"] == 2
    all_saved_ids = [i["_id"] for page in dm.saved for i in page["news_items"]]
    assert all_saved_ids == ["c1", "c2"]


def test_stops_at_previously_synced_id(monkeypatch):
    """EFFECT: pagination stops when the previously synced id is reached."""
    client = _FakeFutmondoClient(
        pages=[
            {
                "news": [
                    {"_id": "c9", "styp": "clause"},
                    {"_id": "prev", "styp": "clause"},
                    {"_id": "c_after", "styp": "clause"},
                ]
            }
        ]
    )
    dm = _RecordingDM(last_sync={"last_sync_id": "prev"})
    service = _make_service(monkeypatch, client, dm)

    result = service.sync_clauses()

    assert result["status"] == "success"
    # Only c9 is collected before hitting the previous id; c_after is never reached.
    assert result["records_synced"] == 1
    assert result["last_sync_id"] == "c9"
    all_saved_ids = [i["_id"] for page in dm.saved for i in page["news_items"]]
    assert all_saved_ids == ["c9"]


# --- Failure modes --------------------------------------------------------
def test_per_page_exception_is_recoverable_break_not_raise(monkeypatch):
    """EFFECT: an ingestion exception inside the loop is caught (log-and-break).

    The outer sync still returns a non-error result (no clauses collected ->
    no_new_data), i.e. the per-page failure degrades gracefully rather than
    propagating.
    """
    client = _FakeFutmondoClient(raises=RuntimeError("page fetch failed"))
    dm = _RecordingDM(last_sync=None)
    service = _make_service(monkeypatch, client, dm)

    result = service.sync_clauses()

    assert result["status"] == "no_new_data"
    assert result["records_synced"] == 0
    assert dm.saved == []
    # Metadata is still written on the (non-error) completion path.
    assert len(dm.metadata) == 1
    assert dm.metadata[0]["sync_status"] == "no_new_data"


def test_outer_exception_is_error(monkeypatch):
    """EFFECT: a failure OUTSIDE the per-page try/except -> status error.

    ``get_last_sync_metadata`` runs before the loop; raising there exercises the
    outer except that records the error status and returns the error payload.
    """

    class _ExplodingDM(_RecordingDM):
        def get_last_sync_metadata(self, championship_id, data_type):
            raise RuntimeError("metadata lookup failed")

    client = _FakeFutmondoClient(pages=[])
    dm = _ExplodingDM(last_sync=None)
    service = _make_service(monkeypatch, client, dm)

    result = service.sync_clauses()

    assert result["status"] == "error"
    assert "metadata lookup failed" in result["error"]
    assert "duration_seconds" in result
    assert dm.saved == []
    assert len(dm.metadata) == 1
    assert dm.metadata[0]["sync_status"] == "error"


def test_error_message_carries_no_credentials(monkeypatch):
    """EFFECT (BR4.2): the error payload never leaks the Futmondo password/token."""

    class _ExplodingDM(_RecordingDM):
        def get_last_sync_metadata(self, championship_id, data_type):
            raise RuntimeError("timeout on /lockerNews")

    client = _FakeFutmondoClient(pages=[])
    dm = _ExplodingDM(last_sync=None)
    service = _make_service(monkeypatch, client, dm)

    result = service.sync_clauses()

    assert result["status"] == "error"
    assert "password" not in result["error"].lower()
    assert "token" not in result["error"].lower()


# --- sync_all ordering ----------------------------------------------------
def test_sync_all_keeps_clauses_key_in_order(monkeypatch):
    """EFFECT (BR3.1): sync_all keeps the literal ``clauses`` key in position.

    Every ``sync_*`` is stubbed to a sentinel so ``sync_all`` runs without DB or
    network; the assertion is on the presence, value routing, and ORDER of the
    ``clauses`` key in the aggregate result.
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

    assert "clauses" in results
    assert results["clauses"] == sentinels["sync_clauses"]
    # Historical key order is preserved: clauses is the 3rd key (index 2).
    keys = list(results.keys())
    assert keys.index("clauses") == 2
    assert len(keys) == 10
    assert keys[-1] == "prizes"
