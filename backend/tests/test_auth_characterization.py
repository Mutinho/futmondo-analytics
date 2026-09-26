"""
Tests de caracterización de AUTH/JWT (FR7.1, FR1.1, FR1.2).

Congelan el comportamiento ACTUAL de:
- `jwt_utils`: emisión/validación de access y refresh tokens, discriminación por
  `type`, expiración y token corrupto.
- `token_store.is_refresh_token_valid`: se ejercita con un doble de conexión
  (sin BD real). El bug de precedencia en la expresión de expiración YA está
  corregido (FR9): un token aware futuro ahora se considera válido. Estos tests
  afirman el contrato CORREGIDO e incluyen la regresión del caso aware pasado.

Prioridad afirmada en team.md: auth es una de las tres áreas prioritarias.
"""

import os
from datetime import datetime, timedelta, timezone

import pytest

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import jwt as pyjwt  # noqa: E402

from app.auth import (
    jwt_utils,  # noqa: E402
    token_store,  # noqa: E402
)

# --- jwt_utils: emisión y validación ---

def test_access_token_roundtrip_carries_claims():
    token = jwt_utils.create_access_token("user-1", "a@b.com", "fm-9")
    payload = jwt_utils.verify_token(token, expected_type="access")
    assert payload is not None
    assert payload["sub"] == "user-1"
    assert payload["email"] == "a@b.com"
    assert payload["futmondo_uid"] == "fm-9"
    assert payload["type"] == "access"
    assert "jti" in payload


def test_refresh_token_roundtrip_and_hash_shape():
    token, token_hash, expires_at = jwt_utils.create_refresh_token("user-1")
    payload = jwt_utils.verify_token(token, expected_type="refresh")
    assert payload is not None
    assert payload["sub"] == "user-1"
    assert payload["type"] == "refresh"
    # El hash almacenado es sha256 hex de 64 chars y coincide con hash_token.
    assert len(token_hash) == 64
    assert jwt_utils.hash_token(token) == token_hash
    assert expires_at > datetime.now(timezone.utc)


def test_verify_token_rejects_wrong_type():
    """Un access token no valida como refresh (discriminación por `type`)."""
    access = jwt_utils.create_access_token("user-1", "a@b.com")
    assert jwt_utils.verify_token(access, expected_type="refresh") is None


def test_verify_token_rejects_garbage():
    assert jwt_utils.verify_token("not-a-jwt", expected_type="access") is None


def test_verify_token_rejects_expired():
    """Un token ya expirado devuelve None (ExpiredSignatureError -> None)."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "user-1",
        "type": "access",
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),
    }
    expired = pyjwt.encode(payload, jwt_utils.JWT_SECRET,
                           algorithm=jwt_utils.JWT_ALGORITHM)
    assert jwt_utils.verify_token(expired, expected_type="access") is None


def test_verify_token_rejects_wrong_signature():
    """Firmado con otro secreto -> inválido."""
    now = datetime.now(timezone.utc)
    payload = {"sub": "user-1", "type": "access",
               "iat": now, "exp": now + timedelta(hours=1)}
    forged = pyjwt.encode(payload, "otro-secreto", algorithm="HS256")
    assert jwt_utils.verify_token(forged, expected_type="access") is None


# --- token_store.is_refresh_token_valid: doble de conexión, sin BD real ---

class _Cursor:
    def __init__(self, row):
        self._row = row
        self.last_sql = None

    def execute(self, sql, params=None):
        self.last_sql = sql
        return self

    def fetchone(self):
        return self._row


class _ConnCtx:
    def __init__(self, row):
        self._row = row

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _FakeDB:
    db_type = "sqlite"

    def __init__(self, row):
        self._row = row
        self.cursor = _Cursor(row)

    def get_connection(self):
        return _ConnCtx(self._row)

    def get_cursor(self, conn):
        return self.cursor

    def adapt_params(self, sql):
        return sql


@pytest.fixture
def patch_db(monkeypatch):
    def _install(row):
        fake = _FakeDB(row)
        monkeypatch.setattr(token_store, "get_db", lambda: fake)
        return fake
    return _install


def test_is_refresh_token_valid_false_when_absent(patch_db):
    patch_db(None)
    assert token_store.is_refresh_token_valid("missing-hash") is False


def test_is_refresh_token_valid_false_when_revoked(patch_db):
    future = (datetime.now(timezone.utc) + timedelta(days=1))
    patch_db((1, future.isoformat()))  # revoked=1
    assert token_store.is_refresh_token_valid("h") is False


def test_is_refresh_token_valid_aware_future_token_returns_true(patch_db):
    """Contrato CORREGIDO (FR9): un token aware futuro es válido.

    Con `expires_at` timezone-aware (lo que produce `.isoformat()` con offset,
    el caso real de PostgreSQL/Neon), la comparación de expiración ahora
    normaliza a aware UTC de forma inequívoca. Un token ACTIVO con expiración
    FUTURA devuelve True.

    CAMBIO DE CONTRATO DELIBERADO: este test antes se llamaba
    `test_is_refresh_token_valid_BUG_aware_future_token_returns_false` y
    congelaba el bug de precedencia (devolvía False). Corregido el código en
    `token_store.is_refresh_token_valid`, el comportamiento esperado cambia a
    True y el test se actualiza de forma trazable (test-after)."""
    future_aware = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    patch_db((0, future_aware))
    assert token_store.is_refresh_token_valid("h") is True


def test_is_refresh_token_valid_aware_past_token_returns_false(patch_db):
    """Regresión del contrato corregido (FR9): aware pasado -> False.

    Camino de error del caso real PostgreSQL/Neon: un token con expiración
    aware ya vencida debe rechazarse."""
    past_aware = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    patch_db((0, past_aware))
    assert token_store.is_refresh_token_valid("h") is False


def test_is_refresh_token_valid_naive_future_token_returns_true(patch_db):
    """Con un timestamp NAIVE futuro, la rama correcta se evalúa y da True.

    Documenta la única entrada bajo la cual hoy un token se considera válido."""
    future_naive = (datetime.now() + timedelta(days=5)).isoformat()  # sin tzinfo
    patch_db((0, future_naive))
    assert token_store.is_refresh_token_valid("h") is True


def test_is_refresh_token_valid_naive_past_token_returns_false(patch_db):
    """Con un timestamp NAIVE ya expirado, la rama correcta rechaza (False)."""
    past_naive = (datetime.now() - timedelta(days=1)).isoformat()
    patch_db((0, past_naive))
    assert token_store.is_refresh_token_valid("h") is False
