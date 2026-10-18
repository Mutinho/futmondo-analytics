"""Tests del transporte del refresh token — bolt `backend-refresh-transport`.

Aseveran el EFECTO del ajuste aditivo que permite a un cliente nativo (sin
cookies de navegador) completar login -> refresh -> logout por header o body,
sin romper el canal cookie `HttpOnly` de la PWA (FR-4, FR-9, NFR-1, NFR-3).

Reglas de la suite (team.md): fakes in-memory (patrón `conftest.py`), sin red,
sin BD real y sin tokens reales. Los tokens se generan en el test con la cripto
real (`jwt_utils.create_refresh_token`) sobre un `JWT_SECRET` efímero fijado en
el entorno antes de importar la app. Nada de `assert True` ni specs espejo: cada
test observa payload/estado.
"""

import os

# Ephemeral, non-default JWT secret fixed BEFORE importing app.core.config so the
# web-service startup guard (NFR1.1) is satisfied and the real crypto signs with
# a known secret. Never a real/production value (gitleaks scans tests).
os.environ.setdefault("JWT_SECRET", "ephemeral-transport-secret-not-default-001")

import pytest  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.auth import routes as auth_routes  # noqa: E402
from app.auth import token_store  # noqa: E402
from app.auth.jwt_utils import create_refresh_token, hash_token, verify_token  # noqa: E402

REFRESH_COOKIE_NAME = "futmondo_refresh_token"


class _FakeDB:
    """In-memory stand-in honoring the ``db_connection`` contract.

    Serves the two reads the transport path performs:
    - ``token_store.is_refresh_token_valid``: ``SELECT revoked, expires_at ...``
    - ``routes.refresh``: ``SELECT futmondo_email, futmondo_user_id FROM app_users``

    Backed by plain dicts seeded per test; no network, no real engine. Datetimes
    are stored ISO-encoded for ``refresh_tokens`` (matching the production
    SQLite/Turso cursor), so ``is_refresh_token_valid`` exercises its real
    normalization branch.
    """

    db_type = "sqlite"

    def __init__(self):
        # user_id -> (futmondo_email, futmondo_user_id)
        self.users: dict[str, tuple[str, str]] = {}
        # token_hash -> {"revoked": int, "expires_at": isoformat str}
        self.refresh_tokens: dict[str, dict] = {}

    # --- db_connection contract ------------------------------------------
    def get_connection(self):
        return _ConnCtx()

    def get_cursor(self, conn):
        return _FakeCursor(self)

    def adapt_params(self, sql: str) -> str:
        return sql


class _ConnCtx:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _FakeCursor:
    """Minimal cursor that answers the two SELECTs the transport path issues."""

    def __init__(self, db: _FakeDB):
        self._db = db
        self._row = None

    def execute(self, sql, params=None):
        normalized = " ".join(sql.split())
        if normalized.startswith("UPDATE refresh_tokens SET revoked"):
            token_hash = params[0]
            record = self._db.refresh_tokens.get(token_hash)
            if record is not None:
                record["revoked"] = 1
            self._row = None
        elif "FROM refresh_tokens" in normalized:
            token_hash = params[0]
            record = self._db.refresh_tokens.get(token_hash)
            self._row = None if record is None else (record["revoked"], record["expires_at"])
        elif "FROM app_users" in normalized:
            user_id = params[0]
            self._row = self._db.users.get(user_id)
        else:
            self._row = None
        return self

    def fetchone(self):
        return self._row

    def fetchall(self):
        return []


def _issue_refresh(db: _FakeDB, user_id: str, email: str):
    """Mint a real refresh token for ``user_id`` and seed the fake stores.

    Returns the token string. Uses the production crypto so the token verifies
    with the ephemeral secret; the user row backs the ``refresh`` lookup.
    """
    token, token_hash, expires_at = create_refresh_token(user_id)
    db.refresh_tokens[token_hash] = {"revoked": 0, "expires_at": expires_at.isoformat()}
    db.users[user_id] = (email, "")
    return token


@pytest.fixture
def fake_db(monkeypatch):
    """Install a fresh in-memory DB for both the token store and the refresh lookup."""
    db = _FakeDB()
    # ``token_store`` reads via its module-level ``get_db``; ``routes.refresh``
    # does a local ``from app.services.db_connection import get_db`` — patch the
    # source module so both resolve to the fake.
    monkeypatch.setattr(token_store, "get_db", lambda: db)
    import app.services.db_connection as db_connection

    monkeypatch.setattr(db_connection, "get_db", lambda: db)

    # refresh() calls get_session_service().ensure_session(...) as a best-effort
    # rehydration. Stub it so the test never reaches real session/DB wiring; a
    # SessionError is the handler's caught, no-op path.
    class _NoopSessionService:
        def ensure_session(self, user_id):
            return None

    monkeypatch.setattr(auth_routes, "get_session_service", lambda: _NoopSessionService())
    return db


@pytest.fixture
def client():
    """A TestClient over a minimal app mounting ONLY the auth router.

    Isolates the transport behavior from the full app wiring (DB pool, cron,
    etc.) while exercising the real route handlers and dependency parsing.
    """
    app = FastAPI()
    app.include_router(auth_routes.router)
    return TestClient(app)


# --- Caso 1: login devuelve refresh_token en body + fija la cookie -----------

def test_login_returns_refresh_token_in_body_and_sets_cookie(client, monkeypatch, fake_db):
    """login() -> el body trae ``refresh_token`` Y la respuesta fija Set-Cookie."""

    class _FakeFutmondoClient:
        def __init__(self, email, password):
            self.user_id = "fm-user-1"

        def login(self):
            return True

    monkeypatch.setattr(auth_routes, "FutmondoClient", _FakeFutmondoClient)
    # Neutralize side effects that touch the real DB/session wiring at login.
    monkeypatch.setattr(auth_routes, "get_user_by_email", lambda email: None)
    monkeypatch.setattr(auth_routes, "upsert_user", lambda **kwargs: None)
    monkeypatch.setattr(auth_routes, "save_refresh_token", lambda *a, **k: None)

    class _FakeStore:
        def store_session(self, *a, **k):
            pass

    monkeypatch.setattr(auth_routes, "get_session_store", lambda: _FakeStore())
    # SessionRepository / session_service best-effort block: force the except path.
    monkeypatch.setattr(auth_routes, "SessionRepository", lambda: (_ for _ in ()).throw(RuntimeError("no db")))
    monkeypatch.setattr(auth_routes, "_auto_detect_championships", lambda *a, **k: None)

    resp = client.post("/auth/login", json={"email": "a@b.com", "password": "x"})

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data.get("refresh_token"), "el body debe incluir refresh_token"
    # La cookie HttpOnly sigue fijándose (no-regresión del canal PWA).
    assert REFRESH_COOKIE_NAME in resp.cookies
    # El token del body debe ser un refresh token válido.
    assert verify_token(data["refresh_token"], expected_type="refresh") is not None


# --- Caso 2: refresh por cookie SIN body -> 200 y NO 422 ---------------------

def test_refresh_by_cookie_without_body_returns_200_not_422(client, fake_db):
    token = _issue_refresh(fake_db, "u-cookie", "cookie@b.com")
    client.cookies.set(REFRESH_COOKIE_NAME, token)

    resp = client.post("/auth/refresh")  # sin body JSON

    assert resp.status_code != 422, "body opcional: una petición sin body no debe dar 422"
    assert resp.status_code == 200, resp.text
    assert resp.json().get("access_token")


# --- Caso 3: refresh por header X-Refresh-Token -> 200 -----------------------

def test_refresh_by_header_returns_200(client, fake_db):
    token = _issue_refresh(fake_db, "u-header", "header@b.com")

    resp = client.post("/auth/refresh", headers={"X-Refresh-Token": token})

    assert resp.status_code == 200, resp.text
    payload = verify_token(resp.json()["access_token"], expected_type="access")
    assert payload is not None and payload["sub"] == "u-header"


# --- Caso 4: refresh por body -> 200 -----------------------------------------

def test_refresh_by_body_returns_200(client, fake_db):
    token = _issue_refresh(fake_db, "u-body", "body@b.com")

    resp = client.post("/auth/refresh", json={"refresh_token": token})

    assert resp.status_code == 200, resp.text
    payload = verify_token(resp.json()["access_token"], expected_type="access")
    assert payload is not None and payload["sub"] == "u-body"


# --- Caso 5: refresh sin token por ningún canal -> 401 -----------------------

def test_refresh_without_token_returns_401(client, fake_db):
    resp = client.post("/auth/refresh")

    assert resp.status_code == 401, resp.text
    assert resp.json()["detail"] == "No refresh token"


# --- Caso 6: logout por header y por body revoca -> refresh posterior 401 ----

def test_logout_by_header_and_body_revokes_then_refresh_401(client, fake_db):
    # 6a) logout por header revoca el token.
    token_header = _issue_refresh(fake_db, "u-logout-h", "lh@b.com")
    resp_logout_h = client.post("/auth/logout", headers={"X-Refresh-Token": token_header})
    assert resp_logout_h.status_code == 200, resp_logout_h.text
    assert fake_db.refresh_tokens[hash_token(token_header)]["revoked"] == 1
    # Un refresh posterior con ese token (por header) debe dar 401 (revocado).
    resp_refresh_h = client.post("/auth/refresh", headers={"X-Refresh-Token": token_header})
    assert resp_refresh_h.status_code == 401
    assert resp_refresh_h.json()["detail"] == "Refresh token revocado"

    # 6b) logout por body revoca el token.
    token_body = _issue_refresh(fake_db, "u-logout-b", "lb@b.com")
    resp_logout_b = client.post("/auth/logout", json={"refresh_token": token_body})
    assert resp_logout_b.status_code == 200, resp_logout_b.text
    assert fake_db.refresh_tokens[hash_token(token_body)]["revoked"] == 1
    resp_refresh_b = client.post("/auth/refresh", json={"refresh_token": token_body})
    assert resp_refresh_b.status_code == 401
    assert resp_refresh_b.json()["detail"] == "Refresh token revocado"


# --- Caso 7: precedencia observable cookie > body ----------------------------

def test_precedence_cookie_wins_over_body_observable_in_access_token(client, fake_db):
    """cookie=T_cookie(U_cookie) + body=T_body(U_body) -> access.sub == U_cookie.

    Observa el canal ganador decodificando el access token devuelto, de modo que
    el test no pueda pasar de forma trivial: si ganara el body, ``sub`` sería
    U_body y el assert fallaría.
    """
    token_cookie = _issue_refresh(fake_db, "U_cookie", "uc@b.com")
    token_body = _issue_refresh(fake_db, "U_body", "ub@b.com")
    assert token_cookie != token_body

    client.cookies.set(REFRESH_COOKIE_NAME, token_cookie)
    resp = client.post("/auth/refresh", json={"refresh_token": token_body})

    assert resp.status_code == 200, resp.text
    payload = verify_token(resp.json()["access_token"], expected_type="access")
    assert payload is not None
    assert payload["sub"] == "U_cookie", "la cookie debe ganar por presencia (BR1)"


# --- Caso 8: borde cookie-revocada + body-válido -> 401 ----------------------

def test_revoked_cookie_with_valid_body_returns_401(client, fake_db):
    """Cookie revocada (presente) + body válido -> 401; gana la cookie (BR1).

    La precedencia es por PRESENCIA, no por validez: la cookie revocada se elige
    y la validación downstream la rechaza; el token del body NO se acepta.
    """
    token_cookie = _issue_refresh(fake_db, "U_revoked", "ur@b.com")
    token_body = _issue_refresh(fake_db, "U_valid_body", "uvb@b.com")
    # Revoca la cookie en el store.
    fake_db.refresh_tokens[hash_token(token_cookie)]["revoked"] = 1

    client.cookies.set(REFRESH_COOKIE_NAME, token_cookie)
    resp = client.post("/auth/refresh", json={"refresh_token": token_body})

    assert resp.status_code == 401, resp.text
    assert resp.json()["detail"] == "Refresh token revocado"
    # El token del body NO fue aceptado: no se emite access token.
    assert "access_token" not in resp.json()
