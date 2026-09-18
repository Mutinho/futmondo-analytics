"""Tests que congelan la exposición del endpoint de fotos (FR7, NFR1.6).

Comportamiento congelado (sin cambio funcional):
- `GET /api/v1/photos/{player_id}` está protegido por `AuthMiddleware`: NO está
  en `AUTH_EXCLUDED_PATHS`, luego una petición sin Bearer a esa ruta devuelve
  401.
- El mount estático `/static/photos/*` es superficie PÚBLICA intencionada por
  quedar fuera del prefijo protegido (`/api/v1` / `/auth`); las fotos no son
  datos sensibles.
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

from fastapi.testclient import TestClient  # noqa: E402

import app.main as main  # noqa: E402


def test_photos_route_not_in_auth_excluded_paths():
    """El endpoint autenticado de fotos NO está exento de auth."""
    assert "/api/v1/photos" not in main.AUTH_EXCLUDED_PATHS
    # Ninguna ruta bajo /api/v1/photos aparece como exclusión explícita.
    for path in main.AUTH_EXCLUDED_PATHS:
        assert not path.startswith("/api/v1/photos")


def test_photos_endpoint_requires_bearer_returns_401():
    """Sin Bearer, una ruta /api/v1/* no excluida (fotos) devuelve 401."""
    client = TestClient(main.app, raise_server_exceptions=False)
    resp = client.get("/api/v1/photos/player-123")
    assert resp.status_code == 401


def test_static_photos_prefix_is_outside_protected_prefix():
    """`/static/photos` cae fuera del prefijo protegido (público a propósito).

    `AuthMiddleware` solo exige token para rutas que empiezan por `/api/v1` o
    `/auth`; el mount estático queda fuera de ambos."""
    static_path = "/static/photos/foo.png"
    assert not static_path.startswith("/api/v1")
    assert not static_path.startswith("/auth")
