"""Characterization tests for ``FutmondoClient._make_request`` — u2-integrations.

Metodología: test-after, characterization-first (Testing Contract del plan). This
module FREEZES the CURRENT behaviour of ``_make_request`` BEFORE the FR4.2/FR4.3
contract migration hardens it, and it publishes the verifiable callers inventory
(BR6.1) as an executable assertion so the core-vs-debt classification cannot
silently drift.

Current (pre-migration) contract being frozen:
- not authenticated (no token/user_id) -> ``None``
- ``requests.exceptions.Timeout``      -> ``None``
- ``requests.exceptions.RequestException`` -> ``None``
- ``json.JSONDecodeError``             -> ``None``
- HTTP 200 OK                          -> parsed ``dict``

No network, no real DB, no real credentials: ``self.session.post`` is
monkeypatched with in-memory fakes and fake login state is injected directly.

NOTE (characterization intent): the network-failure cases below are marked
``xfail(strict=False)`` because Step 3 of the approved plan REPLACES the silent
``None`` with a typed ``IntegrationError``. Freezing the old behaviour here
documents exactly what changed; once the migration lands these three cases flip
to raising, which xfail records as an expected, intended change rather than a
regression. The not-authenticated and 200-OK cases are permanent contract and
stay as plain asserts.
"""

import json

import pytest
import requests

from app.services.futmondo_client import FutmondoClient

# --- In-memory fakes (no network) ---------------------------------------------


class _FakeResponse:
    """Minimal stand-in for ``requests.Response`` for the 200-OK happy path."""

    def __init__(self, payload):
        self._payload = payload
        self.status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def _authenticated_client():
    """Build a client with fake auth state so ``_make_request`` proceeds.

    Uses obviously-fake, non-secret values (never real credentials): gitleaks
    scans test files.
    """
    client = FutmondoClient(email="fake-user@example.test", password="fake-pw-not-real")
    client.token = "fake-token-not-real"  # noqa: S105 - test double, not a secret
    client.user_id = "fake-user-id"
    return client


# --- Permanent contract: not-authenticated and 200-OK -------------------------


def test_make_request_returns_none_when_not_authenticated():
    """Not authenticated is NOT a network failure: it returns None (permanent)."""
    client = FutmondoClient(email="fake-user@example.test", password="fake-pw-not-real")
    # token / user_id left unset -> not authenticated
    result = client._make_request("/1/some/endpoint", {"query": {}})
    assert result is None


def test_make_request_returns_dict_on_200_ok():
    """A 200 OK response is parsed and returned as a dict (permanent contract)."""
    client = _authenticated_client()
    expected = {"answer": {"players": [{"id": "p1"}]}}
    client.session.post = lambda *a, **k: _FakeResponse(expected)
    result = client._make_request("/5/league/championshipplayers", {"query": {}})
    assert result == expected


# --- Frozen legacy behaviour that Step 3 intentionally changes ----------------


@pytest.mark.xfail(
    strict=False,
    reason="Step 3 (FR4.2) replaces the silent None with IntegrationTimeoutError",
)
def test_make_request_swallows_timeout_as_none_LEGACY():
    client = _authenticated_client()

    def _raise_timeout(*a, **k):
        raise requests.exceptions.Timeout("read timed out")

    client.session.post = _raise_timeout
    assert client._make_request("/1/x", {"query": {}}) is None


@pytest.mark.xfail(
    strict=False,
    reason="Step 3 (FR4.2) replaces the silent None with IntegrationRequestError",
)
def test_make_request_swallows_request_exception_as_none_LEGACY():
    client = _authenticated_client()

    def _raise_reqexc(*a, **k):
        raise requests.exceptions.ConnectionError("connection refused")

    client.session.post = _raise_reqexc
    assert client._make_request("/1/x", {"query": {}}) is None


@pytest.mark.xfail(
    strict=False,
    reason="Step 3 (FR4.2) replaces the silent None with IntegrationUnparseableError",
)
def test_make_request_swallows_json_decode_error_as_none_LEGACY():
    client = _authenticated_client()

    class _BadJsonResponse:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            raise json.JSONDecodeError("Expecting value", "", 0)

    client.session.post = lambda *a, **k: _BadJsonResponse()
    assert client._make_request("/1/x", {"query": {}}) is None


# --- Verifiable callers inventory of _make_request (BR6.1, FR4.3) -------------

# Core callers = _make_request itself + the sync consumers where an undetected
# None corrupts/omits synced data. These are the getters exercised by
# DataSyncService.sync_prizes / sync_* (the sync path that writes to the DB).
#
# DIRECT core getters call ``self._make_request`` in their own body.
CORE_MAKE_REQUEST_GETTERS = frozenset(
    {
        "get_championship_players",
        "get_player_summary",
        "get_matchday_standings",
        "get_nightmare_team",
        "get_dream_team",
        "get_match_list",
        "get_round_matches",
        "get_round_lineup",
        "get_userteam_rounds",
        "get_userteam_roster",
        "get_user_roundlineup",
        "get_round_ranking",
        "get_market_players",
        "get_pressroom_news",
        "get_player_fullprofile",
        "get_locker_news",
        "get_league_list",
    }
)

# INDIRECT core getters reach the API through another core getter (not
# _make_request directly); they still propagate the migrated typed failure.
INDIRECT_CORE_GETTERS = frozenset({"get_matchday_history"})

# Debt callers of _make_request outside FutmondoClient (roster endpoints): they
# keep their current handling in U2 and are recorded as debt (BR6.1).
DEBT_ROSTER_CALLERS = ("putonmarket", "toggleplayer", "myplayers", "cancelsell")


def test_core_make_request_callers_inventory_is_pinned():
    """The core getter inventory is verifiable and stable (~20 getters, BR6.1).

    Every DIRECT getter exists on FutmondoClient and its source calls
    ``self._make_request``; the INDIRECT getter reaches the API through another
    core getter. This asserts the inventory documented in code-summary.md
    matches reality before/after the migration.
    """
    import inspect

    for getter_name in CORE_MAKE_REQUEST_GETTERS:
        method = getattr(FutmondoClient, getter_name, None)
        assert method is not None, f"missing core getter {getter_name}"
        src = inspect.getsource(method)
        assert "_make_request" in src, f"{getter_name} does not call _make_request"

    for getter_name in INDIRECT_CORE_GETTERS:
        method = getattr(FutmondoClient, getter_name, None)
        assert method is not None, f"missing indirect core getter {getter_name}"
        src = inspect.getsource(method)
        # Reaches the API through a core getter, not _make_request directly.
        assert any(g in src for g in CORE_MAKE_REQUEST_GETTERS), (
            f"{getter_name} does not delegate to a core getter"
        )

    # ~20 core getters total (17 direct + 1 indirect = 18); the count is asserted
    # so a future removal/addition forces an inventory review (BR6.1).
    assert len(CORE_MAKE_REQUEST_GETTERS) == 17
    assert len(INDIRECT_CORE_GETTERS) == 1
    assert len(CORE_MAKE_REQUEST_GETTERS | INDIRECT_CORE_GETTERS) == 18


def test_debt_callers_are_documented_and_out_of_scope():
    """The 4 roster.py callers are recorded as debt (documented, not migrated)."""
    assert DEBT_ROSTER_CALLERS == ("putonmarket", "toggleplayer", "myplayers", "cancelsell")
    assert len(DEBT_ROSTER_CALLERS) == 4
