"""Durable-task persistence layer (u2-durable-sync-tasks).

Narrow repository layer for the single durable-task entity:

* ``sync_task`` (entity ``Task``) — the durable, restart-surviving record of a
  background sync job, keyed by ``task_id``. The database is the authority for
  task existence and concurrency (FR1.4 / FR1.6 / NFR5); the in-memory
  ``TaskManager`` is a best-effort cache only.

Design constraints:

* The database is the authority for state and concurrency; the in-memory cache
  (``TaskManager``) is best-effort (NFR5).
* On startup, tasks left in ``pending``/``running`` by a crash or redeploy are
  marked ``interrupted_by_restart`` — they are NOT resumed automatically
  (FR1.5, out of scope to resume).
* No sensitive data is stored here: only sync metadata, progress, and results.
* All SQL is parameterized. No SQL leaks into routers or the god-files (C3).

The repository accepts an injectable ``db`` (defaulting to the shared
``get_db()`` singleton) so tests substitute an in-memory fake instead of Neon.
JSON columns (``progress``, ``result``) are stored as TEXT via
``json.dumps``/``json.loads`` for portability across SQLite and PostgreSQL.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from app.services.db_connection import get_db

logger = logging.getLogger(__name__)


class DurableTaskStatus:
    """Durable task lifecycle states persisted in ``sync_task``.

    Mirrors the in-memory ``TaskStatus`` and adds ``INTERRUPTED_BY_RESTART`` for
    tasks that were mid-flight when the process stopped (FR1.5).
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED_BY_RESTART = "interrupted_by_restart"


# States that hold a "sync is in progress" claim for uniqueness checks (FR1.6).
ACTIVE_STATUSES = (DurableTaskStatus.PENDING, DurableTaskStatus.RUNNING)


def _utcnow() -> datetime:
    """Return a timezone-aware UTC now (single source of truth for time)."""
    return datetime.now(timezone.utc)


def _as_aware_utc(value) -> Optional[datetime]:
    """Normalize a DB timestamp (str or datetime, naive or aware) to aware UTC."""
    if value is None:
        return None
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _loads(value) -> Any:
    """Decode a JSON TEXT column, tolerating None and already-decoded values."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        # A malformed JSON column is surfaced as None rather than crashing a
        # read; the DB remains the authority and the row stays readable.
        logger.warning("Could not decode JSON task column; returning None")
        return None


@dataclass
class TaskRecord:
    """A durable sync task as persisted in ``sync_task``."""

    task_id: str
    sync_type: str
    championship_id: str
    status: str
    current_step: Optional[str] = None
    progress: dict = field(default_factory=dict)
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Serialize to the same shape the API exposes for a task."""
        return {
            "task_id": self.task_id,
            "sync_type": self.sync_type,
            "championship_id": self.championship_id,
            "status": self.status,
            "current_step": self.current_step,
            "progress": self.progress or {},
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


# --- Idempotent schema (Step 4) ---------------------------------------------


def ensure_durable_task_schema(db=None) -> None:
    """Create the durable-task table if it does not exist (idempotent).

    Safe to call on every startup: uses ``CREATE TABLE IF NOT EXISTS`` and is a
    no-op when the table already exists. Called from FastAPI startup so a fresh
    Neon database self-provisions, alongside the u1 session schema.
    """
    db = db or get_db()

    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_task (
                task_id TEXT PRIMARY KEY,
                sync_type TEXT NOT NULL,
                championship_id TEXT NOT NULL,
                status TEXT NOT NULL,
                current_step TEXT,
                progress TEXT,
                result TEXT,
                error TEXT,
                created_at TIMESTAMP NOT NULL,
                started_at TIMESTAMP,
                completed_at TIMESTAMP
            )
            """
        )
    logger.info("Durable-task schema ensured (sync_task)")


class TaskRepository:
    """Repository for the durable ``sync_task`` table.

    The database is the authority for task existence and the uniqueness check;
    the in-memory ``TaskManager`` is only a best-effort accelerator.
    """

    def __init__(self, db=None):
        self._db = db or get_db()

    @property
    def _is_pg(self) -> bool:
        return self._db.db_type in ["postgresql", "postgres"]

    def insert(self, task: TaskRecord) -> None:
        """Persist a newly created task (idempotent by ``task_id``).

        Called at trigger time before the worker thread starts, so the task is
        durable the instant it is accepted (FR1.4).
        """
        if not task.task_id or not task.sync_type or not task.championship_id:
            raise ValueError("task_id, sync_type and championship_id are required")

        created_at = task.created_at or _utcnow()
        progress = json.dumps(task.progress or {})
        result = json.dumps(task.result) if task.result is not None else None
        with self._db.get_connection() as conn:
            cursor = self._db.get_cursor(conn)
            if self._is_pg:
                cursor.execute(
                    """
                    INSERT INTO sync_task
                        (task_id, sync_type, championship_id, status, current_step,
                         progress, result, error, created_at, started_at, completed_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (task_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        current_step = EXCLUDED.current_step,
                        progress = EXCLUDED.progress,
                        result = EXCLUDED.result,
                        error = EXCLUDED.error,
                        started_at = EXCLUDED.started_at,
                        completed_at = EXCLUDED.completed_at
                    """,
                    (
                        task.task_id,
                        task.sync_type,
                        task.championship_id,
                        task.status,
                        task.current_step,
                        progress,
                        result,
                        task.error,
                        created_at,
                        task.started_at,
                        task.completed_at,
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO sync_task
                        (task_id, sync_type, championship_id, status, current_step,
                         progress, result, error, created_at, started_at, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (task_id) DO UPDATE SET
                        status = excluded.status,
                        current_step = excluded.current_step,
                        progress = excluded.progress,
                        result = excluded.result,
                        error = excluded.error,
                        started_at = excluded.started_at,
                        completed_at = excluded.completed_at
                    """,
                    (
                        task.task_id,
                        task.sync_type,
                        task.championship_id,
                        task.status,
                        task.current_step,
                        progress,
                        result,
                        task.error,
                        created_at,
                        task.started_at,
                        task.completed_at,
                    ),
                )

    def update_status(
        self,
        task_id: str,
        status: str,
        current_step: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ) -> None:
        """Persist a state transition (running/completed/failed) for a task."""
        if not task_id:
            raise ValueError("task_id is required to update task status")
        with self._db.get_connection() as conn:
            cursor = self._db.get_cursor(conn)
            sql = (
                "UPDATE sync_task SET status = ?, current_step = ?, "
                "started_at = COALESCE(?, started_at), "
                "completed_at = COALESCE(?, completed_at) WHERE task_id = ?"
            )
            sql = self._db.adapt_params(sql)
            cursor.execute(sql, (status, current_step, started_at, completed_at, task_id))

    def update_progress(self, task_id: str, current_step: str, progress: dict) -> None:
        """Persist the current step and the accumulated progress map."""
        if not task_id:
            raise ValueError("task_id is required to update task progress")
        with self._db.get_connection() as conn:
            cursor = self._db.get_cursor(conn)
            sql = "UPDATE sync_task SET current_step = ?, progress = ? WHERE task_id = ?"
            sql = self._db.adapt_params(sql)
            cursor.execute(sql, (current_step, json.dumps(progress or {}), task_id))

    def update_result(
        self, task_id: str, result: dict, completed_at: Optional[datetime] = None
    ) -> None:
        """Persist the terminal successful result and mark the task completed."""
        if not task_id:
            raise ValueError("task_id is required to update task result")
        completed = completed_at or _utcnow()
        with self._db.get_connection() as conn:
            cursor = self._db.get_cursor(conn)
            sql = (
                "UPDATE sync_task SET status = ?, result = ?, current_step = NULL, "
                "completed_at = ? WHERE task_id = ?"
            )
            sql = self._db.adapt_params(sql)
            cursor.execute(
                sql,
                (DurableTaskStatus.COMPLETED, json.dumps(result), completed, task_id),
            )

    def update_error(
        self, task_id: str, error: str, completed_at: Optional[datetime] = None
    ) -> None:
        """Persist a terminal failure with its error message."""
        if not task_id:
            raise ValueError("task_id is required to update task error")
        completed = completed_at or _utcnow()
        with self._db.get_connection() as conn:
            cursor = self._db.get_cursor(conn)
            sql = (
                "UPDATE sync_task SET status = ?, error = ?, current_step = NULL, "
                "completed_at = ? WHERE task_id = ?"
            )
            sql = self._db.adapt_params(sql)
            cursor.execute(sql, (DurableTaskStatus.FAILED, error, completed, task_id))

    def get(self, task_id: str) -> Optional[TaskRecord]:
        """Read a task by ``task_id`` from the database (authority), or None."""
        if not task_id:
            return None
        with self._db.get_connection() as conn:
            cursor = self._db.get_cursor(conn)
            sql = (
                "SELECT task_id, sync_type, championship_id, status, current_step, "
                "progress, result, error, created_at, started_at, completed_at "
                "FROM sync_task WHERE task_id = ?"
            )
            sql = self._db.adapt_params(sql)
            cursor.execute(sql, (task_id,))
            row = cursor.fetchone()
            return self._row_to_record(row) if row else None

    def get_active(self, championship_id: str) -> Optional[TaskRecord]:
        """Return the most recent active (pending/running) task for a champ.

        This is the database-backed uniqueness check (FR1.6): a task marked
        ``interrupted_by_restart`` is NOT active, so it never blocks a relaunch.
        """
        if not championship_id:
            return None
        placeholders = ", ".join("?" for _ in ACTIVE_STATUSES)
        with self._db.get_connection() as conn:
            cursor = self._db.get_cursor(conn)
            sql = (
                "SELECT task_id, sync_type, championship_id, status, current_step, "
                "progress, result, error, created_at, started_at, completed_at "
                f"FROM sync_task WHERE championship_id = ? AND status IN ({placeholders}) "
                "ORDER BY created_at DESC"
            )
            sql = self._db.adapt_params(sql)
            cursor.execute(sql, (championship_id, *ACTIVE_STATUSES))
            row = cursor.fetchone()
            return self._row_to_record(row) if row else None

    def mark_interrupted_on_startup(self) -> int:
        """Mark all pending/running tasks as interrupted-by-restart (FR1.5).

        Called once at startup. Any task still ``pending``/``running`` cannot be
        in progress after a fresh boot (the worker thread died with the old
        process), so it is flagged so a client sees an honest terminal state and
        a relaunch is allowed. Tasks are NOT resumed. Returns the row count.
        """
        placeholders = ", ".join("?" for _ in ACTIVE_STATUSES)
        completed = _utcnow()
        with self._db.get_connection() as conn:
            cursor = self._db.get_cursor(conn)
            sql = (
                "UPDATE sync_task SET status = ?, completed_at = ?, "
                "error = ? WHERE status IN (" + placeholders + ")"
            )
            sql = self._db.adapt_params(sql)
            cursor.execute(
                sql,
                (
                    DurableTaskStatus.INTERRUPTED_BY_RESTART,
                    completed,
                    "Interrumpida por reinicio del servicio",
                    *ACTIVE_STATUSES,
                ),
            )
            return cursor.rowcount

    def _row_to_record(self, row) -> TaskRecord:
        """Map a DB row tuple to a ``TaskRecord`` (single decode point)."""
        return TaskRecord(
            task_id=row[0],
            sync_type=row[1],
            championship_id=row[2],
            status=row[3],
            current_step=row[4],
            progress=_loads(row[5]) or {},
            result=_loads(row[6]),
            error=row[7],
            created_at=_as_aware_utc(row[8]),
            started_at=_as_aware_utc(row[9]),
            completed_at=_as_aware_utc(row[10]),
        )
