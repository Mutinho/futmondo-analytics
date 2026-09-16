"""Test-after tests for the durability business logic + security (Step 9).

Covers ``CredentialProtection`` (encryption at rest, redacted material) and
``SessionService.ensure_session`` (cache -> DB -> rehydrate, idempotency,
transient vs unrecoverable). Uses the in-memory persistence fake and fakes for
the Futmondo client so no network or Neon is touched.
"""

import os

import pytest
import requests
from cryptography.fernet import Fernet

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

from app.security.credential_protection import (  # noqa: E402
    SCHEME_ENCRYPTED_CREDENTIAL_V1,
    CredentialProtection,
    CredentialProtectionUnavailable,
    FutmondoSession,
    ReauthMaterial,
)
from app.services.session_service import (  # noqa: E402
    SessionService,
    SessionUnrecoverableError,
    TransientSessionError,
)
from app.stores.session_repository import (  # noqa: E402
    ProtectedCredentialRepository,
    SessionRepository,
    ensure_durable_session_schema,
)

SECRET_PASSWORD = "top-secret-futmondo-pw"


@pytest.fixture
def key():
    return Fernet.generate_key().decode()


@pytest.fixture
def schema(fake_db):
    ensure_durable_session_schema(db=fake_db)
    return fake_db


# --- Fakes ------------------------------------------------------------------


class _FakeFutmondoClient:
    """Stand-in for FutmondoClient: login() outcome is scripted per instance."""

    _script = {}  # email -> "ok" | "invalid" | "transient"
    login_calls = 0  # process-wide count of successful+attempted logins

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.user_id = None
        self.token = None

    def login(self):
        type(self).login_calls += 1
        outcome = _FakeFutmondoClient._script.get(self.email, "ok")
        if outcome == "invalid":
            return False
        if outcome == "transient":
            raise requests.exceptions.ConnectionError("simulated network failure")
        self.user_id = "fm-" + self.email
        self.token = "tok"
        return True

    def is_authenticated(self):
        return self.token is not None


@pytest.fixture(autouse=True)
def patch_client(monkeypatch):
    _FakeFutmondoClient._script = {}
    _FakeFutmondoClient.login_calls = 0
    monkeypatch.setattr("app.security.credential_protection.FutmondoClient", _FakeFutmondoClient)
    return _FakeFutmondoClient


class _FakeCache:
    """Minimal SessionStore stand-in."""

    def __init__(self):
        self._store = {}

    def get_client(self, user_id):
        return self._store.get(user_id)

    def store_reauthenticated(self, user_id, client, email):
        self._store[user_id] = client


# --- CredentialProtection ---------------------------------------------------


def test_protect_stores_ciphertext_not_plaintext(schema, key):
    protection = CredentialProtection(ProtectedCredentialRepository(db=schema), key=key)
    protection.protect("user-1", "a@b.com", SECRET_PASSWORD)
    # Scan the raw stored bytes: the password must never appear in cleartext.
    with schema.get_connection() as conn:
        cursor = schema.get_cursor(conn)
        cursor.execute("SELECT protected_material, scheme FROM protected_credential")
        material, scheme = cursor.fetchone()
    material_bytes = material if isinstance(material, bytes) else bytes(material)
    assert SECRET_PASSWORD.encode() not in material_bytes
    assert b"a@b.com" not in material_bytes
    assert scheme == SCHEME_ENCRYPTED_CREDENTIAL_V1


def test_can_reauthenticate_reflects_presence(schema, key):
    protection = CredentialProtection(ProtectedCredentialRepository(db=schema), key=key)
    assert protection.can_reauthenticate("user-1") is False
    protection.protect("user-1", "a@b.com", SECRET_PASSWORD)
    assert protection.can_reauthenticate("user-1") is True


def test_reauthenticate_rebuilds_session(schema, key):
    protection = CredentialProtection(ProtectedCredentialRepository(db=schema), key=key)
    protection.protect("user-1", "a@b.com", SECRET_PASSWORD)
    session = protection.reauthenticate("user-1")
    assert isinstance(session, FutmondoSession)
    assert session.email == "a@b.com"
    assert session.client.is_authenticated()
    # The rebuilt session must not expose the password anywhere on its surface.
    assert not hasattr(session, "password")


def test_reauthenticate_returns_none_for_invalid_credential(schema, key, patch_client):
    patch_client._script = {"a@b.com": "invalid"}
    protection = CredentialProtection(ProtectedCredentialRepository(db=schema), key=key)
    protection.protect("user-1", "a@b.com", SECRET_PASSWORD)
    assert protection.reauthenticate("user-1") is None


def test_reauthenticate_returns_none_when_absent(schema, key):
    protection = CredentialProtection(ProtectedCredentialRepository(db=schema), key=key)
    assert protection.reauthenticate("ghost") is None


def test_wrong_key_cannot_decrypt(schema, key):
    protection = CredentialProtection(ProtectedCredentialRepository(db=schema), key=key)
    protection.protect("user-1", "a@b.com", SECRET_PASSWORD)
    other = CredentialProtection(
        ProtectedCredentialRepository(db=schema), key=Fernet.generate_key().decode()
    )
    # Undecryptable ciphertext is unrecoverable, surfaced as None (not a crash).
    assert other.reauthenticate("user-1") is None


def test_missing_key_raises_unavailable(schema):
    with pytest.raises(CredentialProtectionUnavailable):
        CredentialProtection(ProtectedCredentialRepository(db=schema), key="")


def test_reauth_material_repr_is_redacted():
    material = ReauthMaterial(email="a@b.com", password=SECRET_PASSWORD)
    assert repr(material) == "<ReauthMaterial redacted>"
    assert str(material) == "<ReauthMaterial redacted>"
    assert SECRET_PASSWORD not in repr(material)
    assert "a@b.com" not in repr(material)


def test_reauth_material_has_no_dict_slot():
    """__slots__ prevents an accidental attribute (and stray secret) landing."""
    material = ReauthMaterial(email="a@b.com", password=SECRET_PASSWORD)
    with pytest.raises(AttributeError):
        material.leaked = "x"  # type: ignore[attr-defined]


# --- SessionService.ensure_session -----------------------------------------


def _make_service(schema, key):
    protection = CredentialProtection(ProtectedCredentialRepository(db=schema), key=key)
    return (
        SessionService(
            session_store=_FakeCache(),
            session_repository=SessionRepository(db=schema),
            credential_protection=protection,
        ),
        protection,
    )


def test_ensure_session_rebuilds_after_restart(schema, key):
    """Cold cache after a restart: rebuild from durable credential."""
    service, protection = _make_service(schema, key)
    protection.protect("user-1", "a@b.com", SECRET_PASSWORD)
    client = service.ensure_session("user-1")
    assert client.is_authenticated()
    # Durable row now exists (was rehydrated + upserted).
    assert SessionRepository(db=schema).get("user-1") is not None


def test_ensure_session_is_idempotent(schema, key):
    service, protection = _make_service(schema, key)
    protection.protect("user-1", "a@b.com", SECRET_PASSWORD)
    first = service.ensure_session("user-1")
    second = service.ensure_session("user-1")  # second call hits the warm cache
    assert first is second


def test_ensure_session_unrecoverable_without_credential(schema, key):
    service, _ = _make_service(schema, key)
    with pytest.raises(SessionUnrecoverableError):
        service.ensure_session("user-with-no-credential")


def test_ensure_session_unrecoverable_on_invalid_credential(schema, key, patch_client):
    patch_client._script = {"a@b.com": "invalid"}
    service, protection = _make_service(schema, key)
    protection.protect("user-1", "a@b.com", SECRET_PASSWORD)
    with pytest.raises(SessionUnrecoverableError):
        service.ensure_session("user-1")


def test_ensure_session_transient_does_not_logout(schema, key, patch_client):
    """A transient failure raises TransientSessionError; handle is preserved."""
    patch_client._script = {"a@b.com": "transient"}
    service, protection = _make_service(schema, key)
    protection.protect("user-1", "a@b.com", SECRET_PASSWORD)
    with pytest.raises(TransientSessionError):
        service.ensure_session("user-1")
    # The encrypted handle survives the transient failure (not destroyed).
    assert protection.can_reauthenticate("user-1") is True


def test_ensure_session_missing_user_id_is_unrecoverable(schema, key):
    service, _ = _make_service(schema, key)
    with pytest.raises(SessionUnrecoverableError):
        service.ensure_session("")


# --- Concurrency: single rehydration per user (R-02 / R-03) -----------------


def test_concurrent_ensure_session_reauthenticates_once(schema, key, patch_client, monkeypatch):
    """Two concurrent ``ensure_session`` calls for the SAME user trigger exactly
    ONE re-authentication.

    ``login()`` is slowed to widen the race window so that, WITHOUT the per-user
    lock in ``SessionService``, both cold-cache callers would slip past the cache
    check and each call ``login()`` (two re-auths). The lock serializes the
    critical section, so the second thread blocks, then observes the warm cache
    inside the lock and reuses the first thread's result (BR1.1/BR1.2
    idempotency, NFR5.2). Closes R-02 and the missing lock/serialization test of
    R-03.
    """
    import sqlite3
    import threading
    import time
    from contextlib import contextmanager
    from datetime import date, datetime

    original_login = _FakeFutmondoClient.login

    def slow_login(self):
        # A real re-auth is a network round-trip; sleeping here makes an
        # unserialized implementation reliably interleave two logins.
        time.sleep(0.2)
        return original_login(self)

    monkeypatch.setattr(_FakeFutmondoClient, "login", slow_login)

    # A cross-thread-capable in-memory DB (the shared conftest ``fake_db`` uses
    # ``check_same_thread=True`` and cannot be touched from worker threads). Its
    # own lock mirrors production connection-pool serialization of a single
    # SQLite connection; the SUT's per-user lock is what we are actually testing.
    class _ThreadSafeFakeCursor:
        def __init__(self, cursor):
            self._cursor = cursor

        @staticmethod
        def _convert(params):
            if params is None:
                return None
            return tuple(p.isoformat() if isinstance(p, (datetime, date)) else p for p in params)

        def execute(self, sql, params=None):
            if params is not None:
                return self._cursor.execute(sql, self._convert(params))
            return self._cursor.execute(sql)

        def fetchone(self):
            return self._cursor.fetchone()

        def fetchall(self):
            return self._cursor.fetchall()

    class _ThreadSafeFakeDB:
        db_type = "sqlite"

        def __init__(self):
            self._conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._db_lock = threading.Lock()

        @contextmanager
        def get_connection(self):
            self._db_lock.acquire()
            try:
                yield self._conn
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise
            finally:
                self._db_lock.release()

        def get_cursor(self, conn):
            return _ThreadSafeFakeCursor(conn.cursor())

        def adapt_params(self, sql):
            return sql

    ts_db = _ThreadSafeFakeDB()
    ensure_durable_session_schema(db=ts_db)

    # Thread-safe cache: concurrent readers/writers on the same user.
    class _ConcurrentCache:
        def __init__(self):
            self._store = {}
            self._lock = threading.Lock()

        def get_client(self, user_id):
            with self._lock:
                return self._store.get(user_id)

        def store_reauthenticated(self, user_id, client, email):
            with self._lock:
                self._store[user_id] = client

    protection = CredentialProtection(ProtectedCredentialRepository(db=ts_db), key=key)
    service = SessionService(
        session_store=_ConcurrentCache(),
        session_repository=SessionRepository(db=ts_db),
        credential_protection=protection,
    )
    protection.protect("user-1", "a@b.com", SECRET_PASSWORD)

    results = {}
    errors = {}

    def worker(idx):
        try:
            results[idx] = service.ensure_session("user-1")
        except Exception as exc:  # capture, assert on the main thread
            errors[idx] = exc

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)

    assert not any(t.is_alive() for t in threads), "worker deadlocked"
    assert not errors, f"ensure_session raised concurrently: {errors}"
    # Exactly one re-authentication happened across both concurrent callers.
    assert _FakeFutmondoClient.login_calls == 1
    # Both callers observe the same rebuilt client (idempotency).
    assert results[0] is results[1]
    assert results[0].is_authenticated()
