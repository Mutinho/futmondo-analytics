"""Test-after tests for the durable-task business logic (Step 9).

Covers ``TaskService``: a task stays queryable after a "restart" (cold cache ->
DB, FR1.4); the uniqueness guard raises against the persisted state (FR1.6) and
allows a relaunch once a task is interrupted-by-restart; the startup sweep marks
orphaned tasks without resuming them (FR1.5); and the database is the authority
while the cache is best-effort (NFR5).

Uses the in-memory persistence fake (``fake_db``) and a fresh, isolated
``TaskManager`` per test as the best-effort cache — never the process singleton,
so tests share no mutable state.
"""

import pytest

from app.services.task_manager import TaskManager
from app.services.task_service import (
    TaskConflictError,
    TaskPersistenceError,
    TaskService,
)
from app.stores.task_repository import (
    DurableTaskStatus,
    TaskRepository,
    ensure_durable_task_schema,
)


@pytest.fixture
def schema(fake_db):
    ensure_durable_task_schema(db=fake_db)
    return fake_db


@pytest.fixture
def service(schema):
    """A service wired to the fake DB and a fresh in-memory cache."""
    return TaskService(repository=TaskRepository(db=schema), cache=TaskManager())


def test_create_persists_and_warms_cache(service, schema):
    """Create writes the durable row (authority) and warms the cache."""
    record = service.create("all", "champ-1")
    # Durable row exists independently of the cache.
    assert TaskRepository(db=schema).get(record.task_id) is not None
    # Cache is warm too (best-effort).
    assert service._cache.get_task(record.task_id) is not None


def test_task_queryable_after_restart(schema):
    """A task created before a "restart" is still queryable from a cold cache.

    Simulates a restart by building a NEW service with an EMPTY cache over the
    same durable store: ``get`` must fall back to the database (FR1.4).
    """
    before = TaskService(repository=TaskRepository(db=schema), cache=TaskManager())
    record = before.create("all", "champ-1")

    # Fresh process: brand-new empty cache, same durable DB.
    after = TaskService(repository=TaskRepository(db=schema), cache=TaskManager())
    assert after._cache.get_task(record.task_id) is None  # cold cache
    got = after.get(record.task_id)
    assert got is not None
    assert got.task_id == record.task_id
    # The DB fallback warmed the cache on the way out.
    assert after._cache.get_task(record.task_id) is not None


def test_get_active_or_conflict_raises_against_db(service):
    """A running task in the DB triggers a conflict for the same champ (FR1.6)."""
    record = service.create("all", "champ-1")
    service.mark_running(record.task_id, step="players")
    with pytest.raises(TaskConflictError) as excinfo:
        service.get_active_or_conflict("champ-1")
    assert excinfo.value.active_task_id == record.task_id


def test_conflict_survives_cold_cache(schema):
    """The uniqueness guard reads the DB, so it holds after a restart (FR1.6)."""
    before = TaskService(repository=TaskRepository(db=schema), cache=TaskManager())
    record = before.create("all", "champ-1")
    before.mark_running(record.task_id)

    after = TaskService(repository=TaskRepository(db=schema), cache=TaskManager())
    with pytest.raises(TaskConflictError):
        after.get_active_or_conflict("champ-1")


def test_no_conflict_for_other_championship(service):
    """An active task for one champ does not block a different champ."""
    record = service.create("all", "champ-1")
    service.mark_running(record.task_id)
    service.get_active_or_conflict("champ-2")  # must not raise


def test_relaunch_allowed_after_interrupted(service):
    """An interrupted-by-restart task is terminal and allows a relaunch (FR1.6)."""
    record = service.create("all", "champ-1")
    service.mark_running(record.task_id)
    # Simulate the startup sweep marking it interrupted.
    service.mark_interrupted_on_startup()
    # No conflict now: the previous task is terminal.
    service.get_active_or_conflict("champ-1")  # must not raise
    # And a relaunch persists a fresh active task.
    new_record = service.create("all", "champ-1")
    assert new_record.task_id != record.task_id


def test_mark_interrupted_on_startup_does_not_resume(service):
    """The startup sweep marks orphaned tasks but never resumes them (FR1.5)."""
    record = service.create("all", "champ-1")
    service.mark_running(record.task_id)

    swept = service.mark_interrupted_on_startup()
    assert swept == 1
    got = service.get(record.task_id)
    # Marked interrupted, not put back to running (no automatic resume).
    assert got.status == DurableTaskStatus.INTERRUPTED_BY_RESTART


def test_db_is_authority_over_cache(service):
    """When cache and DB disagree, updates flow through the DB (authority)."""
    record = service.create("all", "champ-1")
    service.mark_completed(record.task_id, {"players": {"records_synced": 7}})
    # Read straight from the durable store: it reflects the completion.
    persisted = service._repository.get(record.task_id)
    assert persisted.status == DurableTaskStatus.COMPLETED
    assert persisted.result == {"players": {"records_synced": 7}}


def test_progress_accumulates_across_cold_reads(schema):
    """Progress accumulates in the DB even when each update hits a cold cache."""
    svc = TaskService(repository=TaskRepository(db=schema), cache=TaskManager())
    record = svc.create("all", "champ-1")
    svc.mark_running(record.task_id)
    svc.update_progress(record.task_id, "players", {"status": "done"})
    svc.update_progress(record.task_id, "transactions", {"status": "done"})

    persisted = svc._repository.get(record.task_id)
    assert persisted.progress == {
        "players": {"status": "done"},
        "transactions": {"status": "done"},
    }


def test_create_raises_persistence_error_when_store_unavailable():
    """A failed authority write surfaces a typed error, not a silent success."""

    class _BrokenRepo:
        def insert(self, record):
            raise RuntimeError("db down")

    svc = TaskService(repository=_BrokenRepo(), cache=TaskManager())
    with pytest.raises(TaskPersistenceError):
        svc.create("all", "champ-1")


def test_create_rejects_empty_arguments(service):
    """Input validation at the boundary: empty type/champ is rejected."""
    with pytest.raises(ValueError):
        service.create("", "champ-1")
    with pytest.raises(ValueError):
        service.create("all", "")
