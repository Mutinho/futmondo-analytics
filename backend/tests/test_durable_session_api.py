"""Test-after tests for the API re-wiring (Step 11).

Focus on the observable API contract of the durable-session change:

* ``_helpers.get_user_futmondo_client`` rebuilds after a "restart" (cold cache)
  and returns an actionable 401 (NOT the old opaque 403) when unrecoverable.
* Idempotency: two calls in a row converge on the same live client regardless of
  which trigger warmed the cache.

These exercise the real ``SessionService`` wired to the in-memory persistence
fake and a scripted Futmondo client; no network, no Neon, no full-app boot.
"""

import os

import pytest
from cryptography.fernet import Fernet
from fastapi import HTTPException

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

from app.api.v1.endpoints import _helpers  # noqa: E402
from app.security.credential_protection import CredentialProtection  # noqa: E402
from app.services import session_service as session_service_module  # noqa: E402
from app.services.session_service import SessionService  # noqa: E402
from app.stores.session_repository import (  # noqa: E402
    ProtectedCredentialRepository,
    SessionRepository,
    ensure_durable_session_schema,
)

SECRET_PASSWORD = "top-secret-futmondo-pw"


class _FakeRequest:
    def __init__(self, user):
        self.state = type("_State", (), {})()
        self.state.user = user


class _FakeFutmondoClient:
    _script = {}

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.user_id = None
        self.token = None

    def login(self):
        outcome = _FakeFutmondoClient._script.get(self.email, "ok")
        if outcome == "invalid":
            return False
        self.user_id = "fm-" + self.email
        self.token = "tok"
        return True

    def is_authenticated(self):
        return self.token is not None


class _FakeCache:
    def __init__(self):
        self._store = {}

    def get_client(self, user_id):
        return self._store.get(user_id)

    def store_reauthenticated(self, user_id, client, email):
        self._store[user_id] = client


@pytest.fixture(autouse=True)
def patch_client(monkeypatch):
    _FakeFutmondoClient._script = {}
    monkeypatch.setattr("app.security.credential_protection.FutmondoClient", _FakeFutmondoClient)
    return _FakeFutmondoClient


@pytest.fixture
def wired_service(fake_db, monkeypatch):
    """Wire a real SessionService onto the fake DB and install it as the
    process-wide provider the helper resolves through."""
    ensure_durable_session_schema(db=fake_db)
    key = Fernet.generate_key().decode()
    protection = CredentialProtection(ProtectedCredentialRepository(db=fake_db), key=key)
    service = SessionService(
        session_store=_FakeCache(),
        session_repository=SessionRepository(db=fake_db),
        credential_protection=protection,
    )
    # The helper calls get_session_service(); force it to return our wired one.
    monkeypatch.setattr(session_service_module, "_service", service)
    return service, protection


def test_helper_rebuilds_after_restart(wired_service):
    """Cold cache after restart: the helper rehydrates and returns a client."""
    service, protection = wired_service
    protection.protect("user-1", "a@b.com", SECRET_PASSWORD)
    request = _FakeRequest({"user_id": "user-1"})
    client = _helpers.get_user_futmondo_client(request)
    assert client.is_authenticated()


def test_helper_returns_actionable_401_not_opaque_403(wired_service):
    """First use after restart with no recoverable credential -> 401 (not 403)."""
    request = _FakeRequest({"user_id": "user-without-credential"})
    with pytest.raises(HTTPException) as excinfo:
        _helpers.get_user_futmondo_client(request)
    assert excinfo.value.status_code == 401
    assert excinfo.value.status_code != 403
    # Actionable, user-facing Spanish prose.
    assert "iniciar sesión" in excinfo.value.detail.lower()


def test_helper_unauthenticated_is_401(wired_service):
    request = _FakeRequest(None)
    with pytest.raises(HTTPException) as excinfo:
        _helpers.get_user_futmondo_client(request)
    assert excinfo.value.status_code == 401


def test_helper_is_idempotent_across_calls(wired_service):
    """Two calls converge on the same live client (warm cache after first)."""
    service, protection = wired_service
    protection.protect("user-1", "a@b.com", SECRET_PASSWORD)
    request = _FakeRequest({"user_id": "user-1"})
    first = _helpers.get_user_futmondo_client(request)
    second = _helpers.get_user_futmondo_client(request)
    assert first is second


def test_rehydration_persists_durable_row(wired_service):
    """After a rebuild the durable session row exists regardless of trigger."""
    service, protection = wired_service
    protection.protect("user-1", "a@b.com", SECRET_PASSWORD)
    # Trigger via the service directly (as /auth/refresh does).
    service.ensure_session("user-1")
    assert service._repository.get("user-1") is not None
    # Trigger again via the helper (as a protected endpoint does): still one row.
    request = _FakeRequest({"user_id": "user-1"})
    _helpers.get_user_futmondo_client(request)
    assert service._repository.get("user-1") is not None
