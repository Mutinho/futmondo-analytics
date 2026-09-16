"""Test-after tests for the durable-task schema + repository (Steps 5 and 7).

Covers ``ensure_durable_task_schema`` (idempotency) and ``TaskRepository``
(persistence and read by ``task_id``, DB-backed active lookup for the FR1.6
uniqueness check, and the FR1.5 mark-interrupted-on-startup sweep). Uses the
in-memory persistence fake (``fake_db``) so no Neon or network is touched; each
test builds and discards its own store.
"""

from datetime import datetime, timezone

import pytest

from app.stores.task_repository import (
    ACTIVE_STATUSES,
    DurableTaskStatus,
    TaskRecord,
    TaskRepository,
    ensure_durable_task_schema,
)


@pytest.fixture
def schema(fake_db):
    ensure_durable_task_schema(db=fake_db)
    return fake_db


def _record(
    task_id="t-1", championship_id="champ-1", status=DurableTaskStatus.PENDING, sync_type="all"
):
    return TaskRecord(
        task_id=task_id,
        sync_type=sync_type,
        championship_id=championship_id,
        status=status,
        created_at=datetime.now(timezone.utc),
    )


# --- Schema (Step 5) --------------------------------------------------------


def test_ensure_schema_is_idempotent(fake_db):
    """Calling the schema builder twice is a no-op the second time."""
    ensure_durable_task_schema(db=fake_db)
    ensure_durable_task_schema(db=fake_db)  # must not raise
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sync_task'")
        assert cursor.fetchone() is not None


def test_schema_has_expected_columns(schema):
    """The created table exposes the durable-task contract columns."""
    with schema.get_connection() as conn:
        cursor = schema.get_cursor(conn)
        cursor.execute("PRAGMA table_info(sync_task)")
        columns = {row[1] for row in cursor.fetchall()}
    expected = {
        "task_id",
        "sync_type",
        "championship_id",
        "status",
        "current_step",
        "progress",
        "result",
        "error",
        "created_at",
        "started_at",
        "completed_at",
    }
    assert expected <= columns


# --- Repository (Step 7) ----------------------------------------------------


def test_insert_and_get_roundtrip(schema):
    """A persisted task reads back with its identity and status intact."""
    repo = TaskRepository(db=schema)
    repo.insert(_record(task_id="abc123", championship_id="champ-1"))
    got = repo.get("abc123")
    assert got is not None
    assert got.task_id == "abc123"
    assert got.championship_id == "champ-1"
    assert got.status == DurableTaskStatus.PENDING
    assert got.progress == {}


def test_get_missing_returns_none(schema):
    """Reading an unknown task_id (and an empty id) returns None, not a crash."""
    repo = TaskRepository(db=schema)
    assert repo.get("does-not-exist") is None
    assert repo.get("") is None


def test_update_progress_and_result_persist(schema):
    """Progress and terminal result survive round-trip as decoded JSON."""
    repo = TaskRepository(db=schema)
    repo.insert(_record(task_id="t-1"))
    repo.update_status("t-1", DurableTaskStatus.RUNNING, current_step="players")
    repo.update_progress("t-1", "players", {"players": {"status": "done"}})
    repo.update_result("t-1", {"players": {"records_synced": 5}})

    got = repo.get("t-1")
    assert got.status == DurableTaskStatus.COMPLETED
    assert got.progress == {"players": {"status": "done"}}
    assert got.result == {"players": {"records_synced": 5}}
    assert got.current_step is None
    assert got.completed_at is not None


def test_update_error_marks_failed(schema):
    """An error update records a terminal FAILED state with the message."""
    repo = TaskRepository(db=schema)
    repo.insert(_record(task_id="t-1"))
    repo.update_error("t-1", "boom")
    got = repo.get("t-1")
    assert got.status == DurableTaskStatus.FAILED
    assert got.error == "boom"
    assert got.completed_at is not None


def test_get_active_returns_running_task_from_db(schema):
    """A running task is the DB-backed active task for its championship (FR1.6)."""
    repo = TaskRepository(db=schema)
    repo.insert(_record(task_id="t-1", championship_id="champ-1", status=DurableTaskStatus.RUNNING))
    active = repo.get_active("champ-1")
    assert active is not None
    assert active.task_id == "t-1"
    # A different championship has no active task.
    assert repo.get_active("champ-2") is None


def test_get_active_ignores_terminal_and_interrupted(schema):
    """Completed / failed / interrupted tasks never count as active (FR1.6)."""
    repo = TaskRepository(db=schema)
    repo.insert(_record(task_id="done", status=DurableTaskStatus.COMPLETED))
    repo.insert(_record(task_id="failed", status=DurableTaskStatus.FAILED))
    repo.insert(_record(task_id="stale", status=DurableTaskStatus.INTERRUPTED_BY_RESTART))
    assert repo.get_active("champ-1") is None


def test_mark_interrupted_on_startup_sweeps_active(schema):
    """Pending/running tasks become interrupted-by-restart; terminals untouched."""
    repo = TaskRepository(db=schema)
    repo.insert(_record(task_id="pending", status=DurableTaskStatus.PENDING))
    repo.insert(_record(task_id="running", status=DurableTaskStatus.RUNNING))
    repo.insert(_record(task_id="done", status=DurableTaskStatus.COMPLETED))

    swept = repo.mark_interrupted_on_startup()
    assert swept == 2
    assert repo.get("pending").status == DurableTaskStatus.INTERRUPTED_BY_RESTART
    assert repo.get("running").status == DurableTaskStatus.INTERRUPTED_BY_RESTART
    # A user-facing Spanish message is recorded for the interrupted task.
    assert "reinicio" in repo.get("pending").error.lower()
    # A previously completed task is not disturbed.
    assert repo.get("done").status == DurableTaskStatus.COMPLETED


def test_no_sensitive_data_in_persisted_columns(schema):
    """The task table never stores credentials or passwords, only sync metadata."""
    repo = TaskRepository(db=schema)
    repo.insert(_record(task_id="t-1", sync_type="all"))
    repo.update_progress("t-1", "players", {"players": {"records_synced": 3}})
    with schema.get_connection() as conn:
        cursor = schema.get_cursor(conn)
        cursor.execute(
            "SELECT task_id, sync_type, championship_id, progress, result FROM sync_task"
        )
        row = cursor.fetchone()
    blob = " ".join(str(value) for value in row).lower()
    assert "password" not in blob
    assert "jwt_secret" not in blob


def test_active_statuses_contract():
    """The active-status set is exactly pending + running (guards FR1.6 logic)."""
    assert set(ACTIVE_STATUSES) == {DurableTaskStatus.PENDING, DurableTaskStatus.RUNNING}
