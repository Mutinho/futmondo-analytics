"""Characterization tests for ``DataSyncService.sync_transactions`` (safety net).

These freeze the observable behavior of ``sync_transactions`` across the
``transactions`` domain extraction (characterization-first, test-after — see the
approved Testing Contract). They assert the EFFECT: the observable ``SyncResult``
payload (status, keys, ``records_synced``, ``last_sync_id``,
``duration_seconds``), the paginated pressroom ingestion and transaction
filtering (``_player``/``_buyer``/``_seller``), the de-duplication, the
previously-synced-id stop condition, the competing-bids persistence, the
recoverable per-page failure (log-and-break, not raise), the outer failure mode,
that credentials never leak into the error payload, and — critically (R-01) —
the enrichment throttle cadence (``time.sleep(0.5)`` per fullprofile call AND
``time.sleep(5)`` per batch of 20) by spying ``time.sleep``. Never ``assert True``.

No real DB and no network: the Futmondo API client is a deterministic double and
the persistence port is a recording fake. ``time.sleep`` is monkeypatched to a
spy. No credentials appear anywhere.
"""

import os

# ``app.core.config`` hardens JWT startup (NFR1.1): set a non-default secret
# BEFORE importing the app so instantiating the service does not fail at import.
os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import app.services.sync.transactions.orchestrator as orch_mod  # noqa: E402
from app.services.data_sync_service import DataSyncService  # noqa: E402
from app.services.sync.transactions.domain.pricing import (  # noqa: E402
    find_price_at_date,
)

CHAMPIONSHIP_ID = "592416daa3a2dd871a7a9956"


class _RecordingPort:
    """Records the persistence calls the transactions sync makes (no DB).

    ``enrich_market_values`` is driven exactly as the production adapter does: it
    iterates the configured pending rows and calls back ``resolve_market_value``
    (which performs the client fetch + throttle + pure pricing in the
    orchestrator), updating a row when a value comes back.
    """

    def __init__(self, last_sync=None, pending_rows=None):
        self._last_sync = last_sync
        self._pending_rows = list(pending_rows or [])
        self.columns_ensured = 0
        self.last_sync_queries = []
        self.saved = []
        self.bids_calls = []
        self.metadata = []
        self.enriched_updates = []

    def ensure_transaction_columns(self):
        self.columns_ensured += 1

    def get_last_sync_metadata(self, championship_id, data_type):
        self.last_sync_queries.append(
            {"championship_id": championship_id, "data_type": data_type}
        )
        return self._last_sync

    def save_pressroom_transactions(self, championship_id, transaction_items):
        self.saved.append(
            {"championship_id": championship_id, "items": list(transaction_items)}
        )

    def store_bids(self, transaction_items):
        self.bids_calls.append(list(transaction_items))

    def enrich_market_values(self, championship_id, resolve_market_value):
        enriched = 0
        for txn_id, player_id, txn_date, buyer_team_id in self._pending_rows:
            is_market_purchase = buyer_team_id != "market_team"
            value = resolve_market_value(player_id, txn_date, is_market_purchase)
            if value is None:
                continue
            self.enriched_updates.append((txn_id, value))
            enriched += 1
        return enriched

    def update_sync_metadata(self, **kwargs):
        self.metadata.append(kwargs)


class _FakeFutmondoClient:
    """Deterministic double: ``get_pressroom_news`` + ``get_player_fullprofile``."""

    def __init__(self, pages=None, raises=None, profiles=None):
        self._pages = list(pages or [])
        self._raises = raises
        self._profiles = dict(profiles or {})
        self.news_calls = []
        self.profile_calls = []

    def get_pressroom_news(self, championship_id, from_id=None):
        self.news_calls.append({"championship_id": championship_id, "from_id": from_id})
        if self._raises is not None:
            raise self._raises
        if self._pages:
            return self._pages.pop(0)
        return {}

    def get_player_fullprofile(self, player_id):
        self.profile_calls.append(player_id)
        return self._profiles.get(player_id)


def _make_service(monkeypatch, client, port, sleep_spy=None):
    """Build a ``DataSyncService`` with fakes; inject the recording port.

    The thin facade builds a production adapter, so ``sync_transactions`` is
    overridden to inject the recording port while exercising the REAL
    orchestrator (equivalence check).
    """

    def fake_init(self):
        self.dm = object()  # never touched: the port fake replaces persistence
        self.championship_id = CHAMPIONSHIP_ID
        self.league_id = ""
        self.user_id = ""
        self.client = client

    monkeypatch.setattr(DataSyncService, "__init__", fake_init)

    def thin_delegation(self):
        from app.services.sync.transactions import TransactionsSyncOrchestrator

        orchestrator = TransactionsSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            data=port,
        )
        return orchestrator.sync()

    monkeypatch.setattr(DataSyncService, "sync_transactions", thin_delegation)

    # ``time`` is a single shared module object, so patch it exactly once: a
    # second setattr on ``dss.time``/``orch_mod.time`` would clobber the spy.
    if sleep_spy is None:
        monkeypatch.setattr(orch_mod.time, "sleep", lambda *a, **k: None)
    else:
        monkeypatch.setattr(orch_mod.time, "sleep", sleep_spy)
    return DataSyncService()


# --- Happy path -----------------------------------------------------------
def test_success_returns_frozen_payload_and_persists(monkeypatch):
    """EFFECT: two transaction items -> success, records_synced=2, newest id echoed."""
    client = _FakeFutmondoClient(
        pages=[
            {
                "news": [
                    {"_id": "t1", "_player": "p1"},
                    {"_id": "x1"},  # no actor keys -> filtered out
                    {"_id": "t2", "_buyer": "b1"},
                ]
            }
        ]
    )
    port = _RecordingPort(last_sync=None)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_transactions()

    assert result["status"] == "success"
    assert result["records_synced"] == 2
    # newest_transaction_id is the FIRST transaction encountered (t1).
    assert result["last_sync_id"] == "t1"
    assert "duration_seconds" in result
    assert isinstance(result["duration_seconds"], float)
    # Column ALTERs ran once before the loop.
    assert port.columns_ensured == 1
    # Only the two actor items persisted (x1 filtered out).
    assert len(port.saved) == 1
    saved_ids = [i["_id"] for i in port.saved[0]["items"]]
    assert saved_ids == ["t1", "t2"]
    # Metadata recorded success with count + newest id + data type.
    assert len(port.metadata) == 1
    assert port.metadata[0]["sync_status"] == "success"
    assert port.metadata[0]["records_synced"] == 2
    assert port.metadata[0]["data_type"] == "transactions"
    assert port.metadata[0]["last_sync_id"] == "t1"


def test_no_transactions_yields_no_new_data(monkeypatch):
    """EFFECT: a page with no actor items -> no_new_data, zero records."""
    client = _FakeFutmondoClient(pages=[{"news": [{"_id": "x1"}]}])
    port = _RecordingPort(last_sync=None)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_transactions()

    assert result["status"] == "no_new_data"
    assert result["records_synced"] == 0
    assert result["last_sync_id"] == ""
    assert port.saved == []
    assert port.metadata[0]["sync_status"] == "no_new_data"


def test_bids_are_stored_for_saved_batch(monkeypatch):
    """EFFECT: store_bids is invoked with the saved transaction batch."""
    client = _FakeFutmondoClient(
        pages=[{"news": [{"_id": "t1", "_player": "p1", "bids": [{"bid": 10}]}]}]
    )
    port = _RecordingPort(last_sync=None)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_transactions()

    assert result["status"] == "success"
    assert len(port.bids_calls) == 1
    assert [i["_id"] for i in port.bids_calls[0]] == ["t1"]


def test_dedup_across_pages(monkeypatch):
    """EFFECT: a repeated transaction ``_id`` across pages is persisted only once."""
    client = _FakeFutmondoClient(
        pages=[
            {"news": [{"_id": "t1", "_player": "p1"}, {"_id": "zz", "_buyer": "b"}]},
            {"news": [{"_id": "t1", "_player": "p1"}, {"_id": "t2", "_seller": "s"}]},
        ]
    )
    port = _RecordingPort(last_sync=None)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_transactions()

    assert result["status"] == "success"
    all_saved_ids = [i["_id"] for page in port.saved for i in page["items"]]
    assert all_saved_ids == ["t1", "zz", "t2"]
    assert result["records_synced"] == 3


def test_stops_at_previously_synced_id(monkeypatch):
    """EFFECT: pagination stops when the previously synced id is reached."""
    client = _FakeFutmondoClient(
        pages=[
            {
                "news": [
                    {"_id": "t9", "_player": "p9"},
                    {"_id": "prev", "_player": "pp"},
                    {"_id": "t_after", "_player": "pa"},
                ]
            }
        ]
    )
    port = _RecordingPort(last_sync={"last_sync_id": "prev"})
    service = _make_service(monkeypatch, client, port)

    result = service.sync_transactions()

    assert result["status"] == "success"
    assert result["records_synced"] == 1
    assert result["last_sync_id"] == "t9"
    all_saved_ids = [i["_id"] for page in port.saved for i in page["items"]]
    assert all_saved_ids == ["t9"]


# --- Enrichment throttle cadence (R-01) -----------------------------------
def test_enrichment_throttle_cadence_is_preserved(monkeypatch):
    """EFFECT (R-01): 0.5s after EACH fullprofile call AND 5s per batch of 20.

    25 pending rows for 25 distinct players force 25 API calls, so there must be
    exactly 25 0.5s sleeps and exactly one 5s sleep (after the 20th call).
    """
    profiles = {
        f"pl{i}": {"prices": [{"date": "2026-01-10T00:00:00Z", "social": 100 + i}]}
        for i in range(25)
    }
    pending_rows = [
        (f"txn{i}", f"pl{i}", "2026-01-10T00:00:00Z", "market_team") for i in range(25)
    ]
    client = _FakeFutmondoClient(pages=[], profiles=profiles)
    port = _RecordingPort(last_sync=None, pending_rows=pending_rows)

    sleeps = []
    service = _make_service(
        monkeypatch, client, port, sleep_spy=lambda s: sleeps.append(s)
    )

    result = service.sync_transactions()

    assert result["status"] == "no_new_data"
    assert len(client.profile_calls) == 25
    assert len(port.enriched_updates) == 25
    assert sleeps.count(0.5) == 25
    assert sleeps.count(5) == 1


def test_enrichment_caches_repeated_player(monkeypatch):
    """EFFECT: a repeated ``player_id`` costs neither a 2nd call nor a 2nd sleep."""
    profiles = {"pA": {"prices": [{"date": "2026-01-10T00:00:00Z", "social": 500}]}}
    pending_rows = [
        ("txn1", "pA", "2026-01-10T00:00:00Z", "market_team"),
        ("txn2", "pA", "2026-01-10T00:00:00Z", "market_team"),
    ]
    client = _FakeFutmondoClient(pages=[], profiles=profiles)
    port = _RecordingPort(last_sync=None, pending_rows=pending_rows)

    sleeps = []
    service = _make_service(
        monkeypatch, client, port, sleep_spy=lambda s: sleeps.append(s)
    )

    service.sync_transactions()

    assert client.profile_calls == ["pA"]
    assert sleeps.count(0.5) == 1
    assert len(port.enriched_updates) == 2


# --- Failure modes --------------------------------------------------------
def test_per_page_exception_is_recoverable_break_not_raise(monkeypatch):
    """EFFECT: an ingestion exception inside the loop is caught (log-and-break)."""
    client = _FakeFutmondoClient(raises=RuntimeError("page fetch failed"))
    port = _RecordingPort(last_sync=None)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_transactions()

    assert result["status"] == "no_new_data"
    assert result["records_synced"] == 0
    assert port.saved == []
    assert port.metadata[0]["sync_status"] == "no_new_data"


def test_outer_exception_is_error(monkeypatch):
    """EFFECT: a failure OUTSIDE the per-page try/except -> status error."""

    class _ExplodingPort(_RecordingPort):
        def get_last_sync_metadata(self, championship_id, data_type):
            raise RuntimeError("metadata lookup failed")

    client = _FakeFutmondoClient(pages=[])
    port = _ExplodingPort(last_sync=None)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_transactions()

    assert result["status"] == "error"
    assert "metadata lookup failed" in result["error"]
    assert "duration_seconds" in result
    assert port.saved == []
    assert port.metadata[0]["sync_status"] == "error"


def test_error_message_carries_no_credentials(monkeypatch):
    """EFFECT (BR4.2): the error payload never leaks the Futmondo password/token."""

    class _ExplodingPort(_RecordingPort):
        def get_last_sync_metadata(self, championship_id, data_type):
            raise RuntimeError("timeout on /pressroom")

    client = _FakeFutmondoClient(pages=[])
    port = _ExplodingPort(last_sync=None)
    service = _make_service(monkeypatch, client, port)

    result = service.sync_transactions()

    assert result["status"] == "error"
    assert "password" not in result["error"].lower()
    assert "token" not in result["error"].lower()


# --- Pure pricing helper --------------------------------------------------
def test_find_price_at_date_prefers_same_day_for_sales():
    """EFFECT: non-previous-day match picks the same-day social price."""
    prices = [
        {"date": "2026-01-09T00:00:00Z", "social": 90},
        {"date": "2026-01-10T00:00:00Z", "social": 100},
    ]
    assert find_price_at_date(prices, "2026-01-10T00:00:00Z") == 100


def test_find_price_at_date_prefers_previous_day_for_market_purchase():
    """EFFECT: prefer_previous_day picks the day-before social price."""
    prices = [
        {"date": "2026-01-09T00:00:00Z", "social": 90},
        {"date": "2026-01-10T00:00:00Z", "social": 100},
    ]
    assert (
        find_price_at_date(prices, "2026-01-10T00:00:00Z", prefer_previous_day=True)
        == 90
    )


def test_find_price_at_date_window_and_fallback():
    """EFFECT: entries older than 3 days are ignored; missing social falls to classic."""
    prices = [
        {"date": "2026-01-01T00:00:00Z", "social": 50},  # 9 days before -> ignored
        {"date": "2026-01-09T00:00:00Z", "classic": 77},  # within window, no social
    ]
    assert find_price_at_date(prices, "2026-01-10T00:00:00Z") == 77


# --- sync_all ordering ----------------------------------------------------
def test_sync_all_keeps_transactions_key_in_order(monkeypatch):
    """EFFECT (BR3.1): sync_all keeps the literal ``transactions`` key in position."""
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

    assert "transactions" in results
    assert results["transactions"] == sentinels["sync_transactions"]
    keys = list(results.keys())
    assert keys.index("transactions") == 1
    assert len(keys) == 10
    assert keys[-1] == "prizes"
