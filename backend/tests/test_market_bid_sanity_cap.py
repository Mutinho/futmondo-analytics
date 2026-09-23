"""Tests dirigidos del techo de cordura de `price` en `place_bid` (FR6 / BR4).

Congelan el guardarraíl de backend contra un `price` absurdo/overflow: un precio
por encima de `PRICE_SANITY_CAP` se rechaza en el boundary con 422 ANTES de
resolver el cliente Futmondo o producir cualquier efecto lateral. Se mantienen
sin regresión las reglas ya existentes: `price <= 0` -> 422; un `price` válido
intermedio -> 200 e invoca al cliente.

Se monta el router `market` en una FastAPI mínima (mismo patrón que
`test_market_bid_validation.py`) y se parchea `get_user_futmondo_client` con un
doble espía; no hay BD ni red reales.
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import pytest  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app.api.v1.endpoints._helpers as helpers  # noqa: E402
import app.api.v1.endpoints.market as market  # noqa: E402


class _SpyClient:
    """Futmondo client double that records whether the bid was posted."""

    def __init__(self):
        self.user_id = "fm-user-1"
        self.token = "fake-token"
        self.base_url = "https://api.example.test"
        self.session = self
        self.posted = False

    def post(self, url, json=None, timeout=None):  # noqa: A002 - mirror requests API
        self.posted = True
        return _FakeResponse({"answer": {"code": "api.general.ok"}})


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload
        self.status_code = 200

    def json(self):
        return self._payload


def _client():
    application = FastAPI()
    application.include_router(market.router, prefix="/api/v1/market")
    return TestClient(application, raise_server_exceptions=False)


@pytest.fixture
def spy_client(monkeypatch):
    """Install a spy Futmondo client and a valid team id; return the spy."""
    spy = _SpyClient()
    monkeypatch.setattr(helpers, "get_user_futmondo_client", lambda request: spy)
    monkeypatch.setattr(market, "_get_user_team_id", lambda client, cid: "team-1")
    return spy


def _bid_url(price):
    return f"/api/v1/market/bid?championship_id=c1&player_id=p1&player_slug=slug&price={price}"


def test_bid_price_above_cap_returns_422_and_client_not_called(spy_client):
    resp = _client().post(_bid_url(market.PRICE_SANITY_CAP + 1))
    assert resp.status_code == 422
    assert spy_client.posted is False


def test_bid_price_at_cap_is_allowed_and_invokes_client(spy_client):
    # The cap is inclusive: exactly at the ceiling is still a valid bid.
    resp = _client().post(_bid_url(market.PRICE_SANITY_CAP))
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert spy_client.posted is True


def test_bid_price_zero_still_returns_422_no_regression(spy_client):
    resp = _client().post(_bid_url(0))
    assert resp.status_code == 422
    assert spy_client.posted is False


def test_bid_price_intermediate_valid_invokes_client(spy_client):
    resp = _client().post(_bid_url(1_000_000))
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert spy_client.posted is True
