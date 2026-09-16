"""Test-after tests for the sync API re-wiring (Step 11).

Focus on the observable API contract of the durable-task change:

* ``GET /api/v1/sync/task/{id}`` returns a task's state after a "restart"
  (cold cache -> DB, FR1.4).
* ``POST /api/v1/sync/trigger`` returns 409 against the PERSISTED active state
  (FR1.6) and allows a relaunch once the previous task is interrupted-by-restart.
* A task left running by the previous process shows up as interrupted after the
  startup sweep.

These wire a real ``TaskService`` onto the in-memory persistence fake and mock
both the Futmondo client resolution and the background sync worker, so no
network, no Neon, and no real sync run. The auth middleware is bypassed by
calling the endpoint coroutines directly with a fake request, mirroring the u1
API tests' style (no full-app boot needed for the durability contract).
"""

import asyncio
import os

import pytest
from fastapi import HTTPException

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000000000000")

from app.api.v1.endpoints import sync as sync_module  # noqa: E402
from app.services.task_manager import TaskManager  # noqa: E402
from app.services.task_service import TaskService  # noqa: E402
from app.stores.task_repository import (  # noqa: E402
    DurableTaskStatus,
    TaskRepository,
    ensure_durable_task_schema,
)


class _FakeRequest:
    """Minimal Request stand-in exposing ``state.user`` like the middleware."""

    def __init__(self, user_id="user-1"):
        self.state = type("_State", (), {})()
        self.state.user = {"user_id": user_id}


class _FakeClient:
    def is_authenticated(self):
        return True


@pytest.fixture
def wired(fake_db, monkeypatch):
    """Wire a real TaskService onto the fake DB as the process-wide provider,
    and neutralize the client resolution + background worker."""
    ensure_durable_task_schema(db=fake_db)
    service = TaskService(repository=TaskRepository(db=fake_db), cache=TaskManager())
    monkeypatch.setattr(sync_module, "get_task_service", lambda: service)

    # The /trigger endpoint resolves a Futmondo client via a lazily-imported
    # helper; stub it so no session/network is needed.
    import app.api.v1.endpoints._helpers as helpers

    monkeypatch.setattr(helpers, "get_user_futmondo_client", lambda request: _FakeClient())

    # Do not actually run a sync in a background thread during the test.
    started = {}

    class _FakeThread:
        def __init__(self, target=None, args=(), daemon=None):
            started["args"] = args

        def start(self):
            started["started"] = True

    monkeypatch.setattr(sync_module.threading, "Thread", _FakeThread)
    return service, started


def _run(coro):
    return asyncio.run(coro)


def test_task_endpoint_returns_state_after_restart(wired, monkeypatch):
    """GET /task/{id} returns the persisted state from a cold cache (FR1.4)."""
    service, _ = wired
    record = service.create("all", "champ-1")
    service.mark_running(record.task_id, step="players")

    # Simulate a restart: a service with an EMPTY cache over the same durable
    # store, installed as the endpoint's provider.
    cold = TaskService(repository=service._repository, cache=TaskManager())
    assert cold._cache.get_task(record.task_id) is None
    monkeypatch.setattr(sync_module, "get_task_service", lambda: cold)

    result = _run(sync_module.get_task_status(record.task_id))
    assert result["success"] is True
    assert result["task_id"] == record.task_id
    assert result["status"] == DurableTaskStatus.RUNNING


def test_task_endpoint_404_for_unknown(wired):
    """GET /task/{id} raises 404 for an unknown task id."""
    with pytest.raises(HTTPException) as excinfo:
        _run(sync_module.get_task_status("does-not-exist"))
    assert excinfo.value.status_code == 404


def test_trigger_returns_409_against_persisted_state(wired):
    """POST /trigger returns 409 when a persisted task is active (FR1.6)."""
    service, _ = wired
    existing = service.create("all", "12345")
    service.mark_running(existing.task_id)

    response = _run(
        sync_module.trigger_sync(_FakeRequest(), sync_type="all", championship_id="12345")
    )
    assert response.status_code == 409
    import json

    body = json.loads(response.body)
    assert body["success"] is False
    assert body["task_id"] == existing.task_id


def test_trigger_starts_when_no_active_task(wired):
    """POST /trigger accepts (202) and persists a task when none is active."""
    service, started = wired
    response = _run(
        sync_module.trigger_sync(_FakeRequest(), sync_type="all", championship_id="12345")
    )
    assert response.status_code == 202
    import json

    body = json.loads(response.body)
    task_id = body["task_id"]
    # The task is durable immediately (queryable before the worker runs).
    assert service.get(task_id) is not None
    # A worker thread was launched with the new task id.
    assert started.get("started") is True
    assert started["args"][0] == task_id


def test_trigger_relaunches_after_interrupted(wired):
    """A previously-running task interrupted by restart no longer blocks (FR1.6)."""
    service, _ = wired
    old = service.create("all", "12345")
    service.mark_running(old.task_id)
    # Startup sweep marks it interrupted-by-restart.
    service.mark_interrupted_on_startup()
    assert service.get(old.task_id).status == DurableTaskStatus.INTERRUPTED_BY_RESTART

    # Relaunch is now allowed (202), and a fresh task id is minted.
    response = _run(
        sync_module.trigger_sync(_FakeRequest(), sync_type="all", championship_id="12345")
    )
    assert response.status_code == 202
    import json

    body = json.loads(response.body)
    assert body["task_id"] != old.task_id


def test_trigger_rejects_invalid_sync_type(wired):
    """POST /trigger validates sync_type at the boundary (400)."""
    with pytest.raises(HTTPException) as excinfo:
        _run(sync_module.trigger_sync(_FakeRequest(), sync_type="nope", championship_id="12345"))
    assert excinfo.value.status_code == 400
