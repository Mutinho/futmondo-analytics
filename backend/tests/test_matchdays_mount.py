"""
Tests for FR15.1: matchdays router is mounted only under the canonical prefix.

Asserts the EFFECT of unifying the mount via the HTTP surface (no network, no
real DB, no credentials — the TestClient drives the app in-process):

- The canonical ``/api/v1/matchdays/*`` route EXISTS: an unauthenticated request
  is rejected by ``AuthMiddleware`` with 401 (the route matched; auth blocked it),
  never 404. This is the happy-path proof that the endpoint remains reachable
  (FR15.1.1).
- The retired ``/v1/matchdays/*`` prefix is GONE: a request to it returns 404
  (no route matches), confirming the duplicate mount was removed (FR15.1.2).
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)

_CANONICAL_PATH = "/api/v1/matchdays/teams"
_RETIRED_PATH = "/v1/matchdays/teams"


def test_canonical_matchdays_route_exists_and_requires_auth():
    """The canonical route matches (401 from auth), proving it is still mounted
    and reachable (FR15.1.1). A 404 here would mean the mount was lost."""
    resp = client.get(_CANONICAL_PATH)
    assert resp.status_code == 401, (
        f"expected 401 (route mounted, auth-protected); got {resp.status_code}"
    )


def test_retired_v1_matchdays_prefix_is_gone():
    """The non-canonical /v1/matchdays mount was removed: no route matches, so
    the auth middleware never even runs for it → 404 (FR15.1.2)."""
    resp = client.get(_RETIRED_PATH)
    assert resp.status_code == 404, (
        f"expected 404 (retired prefix removed); got {resp.status_code}"
    )
