"""Narrow persistence layer for durable session state (u1-durable-session).

This package isolates all SQL for the durable-session feature behind a thin
repository API. It reuses the shared ``db_connection`` abstractor and never
adds SQL to routers or the god-files (``data_manager_v2``,
``data_sync_service``). All queries are parameterized.
"""

from app.stores.session_repository import (
    ProtectedCredentialRecord,
    ProtectedCredentialRepository,
    SessionRecord,
    SessionRepository,
    ensure_durable_session_schema,
)
from app.stores.task_repository import (
    DurableTaskStatus,
    TaskRecord,
    TaskRepository,
    ensure_durable_task_schema,
)

__all__ = [
    "SessionRecord",
    "SessionRepository",
    "ProtectedCredentialRecord",
    "ProtectedCredentialRepository",
    "ensure_durable_session_schema",
    "TaskRecord",
    "TaskRepository",
    "DurableTaskStatus",
    "ensure_durable_task_schema",
]
