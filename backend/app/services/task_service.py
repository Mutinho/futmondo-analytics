"""Durable-task business logic (u2-durable-sync-tasks, Step 8).

``TaskService`` is the seam between the sync endpoints/worker and the durable
``sync_task`` table. It enforces the durability contract:

* **Create** persists the task first (authority) and then warms the in-memory
  ``TaskManager`` cache (best-effort), so a task is durable the instant it is
  accepted (FR1.4).
* **State/progress updates** write the database (authority) and mirror the
  in-memory cache (best-effort) — a cache miss never loses state (NFR5).
* **Get** reads the cache first for speed, then falls back to the database, so a
  task stays queryable after a restart with a cold cache (FR1.4).
* **Uniqueness** (``get_active_or_conflict``) is checked against the database,
  not the process cache, so a second instance or a restarted one still refuses a
  duplicate sync — except a task left ``interrupted_by_restart``, which is
  terminal and allows a relaunch (FR1.6).
* **Startup sweep** (``mark_interrupted_on_startup``) marks orphaned in-flight
  tasks as interrupted; it does NOT resume them (FR1.5, out of scope).

The service takes injectable collaborators (repository, cache) so tests wire an
in-memory persistence fake and a fake cache with no Neon or network.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.services.task_manager import Task, TaskManager, get_task_manager
from app.stores.task_repository import (
    DurableTaskStatus,
    TaskRecord,
    TaskRepository,
)

logger = logging.getLogger(__name__)


class TaskConflictError(Exception):
    """Raised when a sync is already active for a championship (FR1.6, 409)."""

    def __init__(self, active_task_id: str, championship_id: str):
        self.active_task_id = active_task_id
        self.championship_id = championship_id
        super().__init__(
            f"A sync is already active for championship {championship_id} (task {active_task_id})"
        )


class TaskPersistenceError(Exception):
    """Raised when the durable store cannot satisfy an authoritative operation."""


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _record_to_cache_task(record: TaskRecord) -> Task:
    """Rebuild an in-memory ``Task`` from a durable record (cache warming)."""
    task = Task(record.task_id, record.sync_type, record.championship_id)
    task.status = record.status
    task.current_step = record.current_step
    task.progress = record.progress or {}
    task.result = record.result
    task.error = record.error
    if record.created_at:
        task.created_at = record.created_at
    task.started_at = record.started_at
    task.completed_at = record.completed_at
    return task


class TaskService:
    """Durability-aware coordinator over ``TaskRepository`` and ``TaskManager``.

    The database is the authority; the ``TaskManager`` cache is best-effort.
    """

    def __init__(
        self,
        repository: Optional[TaskRepository] = None,
        cache: Optional[TaskManager] = None,
    ):
        self._repository = repository or TaskRepository()
        self._cache = cache or get_task_manager()

    # --- Create -------------------------------------------------------------

    def create(self, sync_type: str, championship_id: str) -> TaskRecord:
        """Persist a new task (authority) and warm the cache (best-effort).

        The database write is mandatory — if it fails the task is not accepted.
        The cache write is best-effort and never fails the operation (NFR5).
        """
        if not sync_type or not championship_id:
            raise ValueError("sync_type and championship_id are required")

        task_id = uuid.uuid4().hex[:12]
        record = TaskRecord(
            task_id=task_id,
            sync_type=sync_type,
            championship_id=championship_id,
            status=DurableTaskStatus.PENDING,
            progress={},
            created_at=_utcnow(),
        )
        try:
            self._repository.insert(record)
        except Exception as exc:  # authority write must succeed
            raise TaskPersistenceError(
                f"Could not persist sync task for championship {championship_id}"
            ) from exc

        self._warm_cache(record)
        return record

    # --- Uniqueness (FR1.6) -------------------------------------------------

    def get_active_or_conflict(self, championship_id: str) -> None:
        """Raise ``TaskConflictError`` if a sync is already active (FR1.6).

        Checked against the database so the guard survives a restart and holds
        across instances. A task left ``interrupted_by_restart`` is terminal and
        does NOT block a relaunch.
        """
        active = self._repository.get_active(championship_id)
        if active is not None:
            raise TaskConflictError(active.task_id, championship_id)

    # --- State / progress updates (authority + best-effort cache) -----------

    def mark_running(self, task_id: str, step: Optional[str] = None) -> None:
        """Transition a task to running in the DB, then mirror the cache."""
        self._repository.update_status(
            task_id,
            DurableTaskStatus.RUNNING,
            current_step=step,
            started_at=_utcnow(),
        )
        self._cache_call(lambda: self._cache.mark_running(task_id, step))

    def update_progress(self, task_id: str, step: str, data: Optional[dict] = None) -> None:
        """Persist the accumulated progress map, then mirror the cache.

        The progress map is read-modify-written against the durable record so a
        cold cache after a restart still accumulates correctly (DB authority).
        """
        record = self._repository.get(task_id)
        progress = dict(record.progress) if record and record.progress else {}
        if data is not None:
            progress[step] = data
        self._repository.update_progress(task_id, step, progress)
        self._cache_call(lambda: self._cache.update_progress(task_id, step, data))

    def mark_completed(self, task_id: str, result: dict) -> None:
        """Persist the terminal result, then mirror the cache."""
        self._repository.update_result(task_id, result, completed_at=_utcnow())
        self._cache_call(lambda: self._cache.mark_completed(task_id, result))

    def mark_failed(self, task_id: str, error: str) -> None:
        """Persist a terminal failure, then mirror the cache."""
        self._repository.update_error(task_id, error, completed_at=_utcnow())
        self._cache_call(lambda: self._cache.mark_failed(task_id, error))

    # --- Read (cache -> DB, FR1.4) ------------------------------------------

    def get(self, task_id: str) -> Optional[TaskRecord]:
        """Return a task as a ``TaskRecord``, cache-first then database (FR1.4).

        After a restart the cache is cold, so this falls back to the database and
        warms the cache on the way out, keeping ``/task/{id}`` queryable.
        """
        if not task_id:
            return None

        cached = self._cache.get_task(task_id)
        if cached is not None:
            return self._cache_task_to_record(cached)

        record = self._repository.get(task_id)
        if record is not None:
            self._warm_cache(record)
        return record

    # --- Startup sweep (FR1.5) ----------------------------------------------

    def mark_interrupted_on_startup(self) -> int:
        """Mark orphaned in-flight tasks interrupted-by-restart (FR1.5).

        Does NOT resume any task; resumption is out of scope. Invalidates the
        best-effort cache afterwards so a stale in-flight entry never masks the
        authoritative interrupted state on a subsequent read (NFR5). Returns the
        number of tasks swept.
        """
        swept = self._repository.mark_interrupted_on_startup()
        self._cache_call(self._cache.clear)
        return swept

    # --- Internal helpers ---------------------------------------------------

    def _warm_cache(self, record: TaskRecord) -> None:
        """Best-effort: mirror a durable record into the in-memory cache."""
        self._cache_call(lambda: self._cache.put(_record_to_cache_task(record)))

    def _cache_call(self, action) -> None:
        """Run a best-effort cache mutation, swallowing only cache failures.

        A cache failure must never fail an operation whose authority already
        succeeded (NFR5). The failure is logged (not silently swallowed) so a
        degraded cache is observable.
        """
        try:
            action()
        except Exception as exc:  # best-effort cache only; DB is authority
            logger.warning("Best-effort task cache update failed: %s", exc)

    @staticmethod
    def _cache_task_to_record(task: Task) -> TaskRecord:
        """Adapt an in-memory ``Task`` to the ``TaskRecord`` return contract."""
        return TaskRecord(
            task_id=task.task_id,
            sync_type=task.sync_type,
            championship_id=task.championship_id,
            status=task.status,
            current_step=task.current_step,
            progress=task.progress or {},
            result=task.result,
            error=task.error,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
        )


# --- Provider singleton -----------------------------------------------------

_task_service: Optional[TaskService] = None


def get_task_service() -> TaskService:
    """Get or create the global ``TaskService`` singleton (DB + shared cache)."""
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service
