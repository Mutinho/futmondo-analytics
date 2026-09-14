"""
Tests de protección de los endpoints destructivos de BD (NFR1.2).

`/api/v1/database/reset` y `/api/v1/database/populate` recrean o borran el
esquema. Deben devolver 404 por defecto (sin exponer su existencia) y solo ser
alcanzables cuando `ENABLE_DB_ADMIN` está activo. Se monta una app FastAPI
mínima con el router; NO se ejecuta el reset real (el DataManager se sustituye
por un doble para el caso habilitado, evitando tocar ninguna BD).
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import pytest  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app.api.v1.endpoints.reset_db as reset_db  # noqa: E402


def _client():
    application = FastAPI()
    application.include_router(reset_db.router, prefix="/api/v1/database")
    return TestClient(application)


@pytest.fixture(autouse=True)
def _clear_flag(monkeypatch):
    monkeypatch.delenv("ENABLE_DB_ADMIN", raising=False)


def test_reset_blocked_by_default_returns_404(monkeypatch):
    resp = _client().post("/api/v1/database/reset")
    assert resp.status_code == 404


def test_populate_blocked_by_default_returns_404(monkeypatch):
    resp = _client().post("/api/v1/database/populate")
    assert resp.status_code == 404


def test_reset_flag_false_value_still_blocked(monkeypatch):
    """Un valor no afirmativo (p.ej. '0') mantiene el bloqueo (404)."""
    monkeypatch.setenv("ENABLE_DB_ADMIN", "0")
    resp = _client().post("/api/v1/database/reset")
    assert resp.status_code == 404


def test_reset_reachable_when_flag_enabled(monkeypatch):
    """Con ENABLE_DB_ADMIN=1 el endpoint pasa el guard (ya no es 404).

    Se sustituye DataManagerV2 por un doble para no tocar ninguna BD real; el
    objetivo es verificar que el guard ya no bloquea, no ejecutar un reset."""
    monkeypatch.setenv("ENABLE_DB_ADMIN", "1")

    class FakeDM:
        def __init__(self, *a, **k):
            pass

        def reset_database(self):
            return None

    monkeypatch.setattr(reset_db, "DataManagerV2", FakeDM)
    resp = _client().post("/api/v1/database/reset")
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
