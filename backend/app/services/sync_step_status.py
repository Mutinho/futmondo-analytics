"""Narrow helper for observable, non-critical sync step degradation.

FR3.1 / BR1-BR2 (unit sync-reliability): a non-critical sync step (``prizes``,
``phantoms``) that raises must be recorded as ``degraded`` — NOT ``done`` with a
buried error — so a reliability consumer (NFR1) can tell a real success from a
partial failure by reading ``progress[step].status``.

This module lives OUTSIDE the sync god-files (NFR2): it is a small, testable
surface reused by the sync worker. Identifiers, comments and docstrings are in
English; user-facing text stays in Spanish (there is none here — this is an
internal state/logging helper).
"""

import logging
from typing import Optional, Protocol

logger = logging.getLogger(__name__)


class StepStatus:
    """Canonical per-step status values written into ``progress[step].status``.

    ``progress`` is a free-form JSON map on both the in-memory ``TaskManager`` and
    the durable ``TaskRecord``; ``DEGRADED`` is the new, additive value (CT2).
    """

    RUNNING = "running"
    DONE = "done"
    DEGRADED = "degraded"


class ProgressSink(Protocol):
    """Structural type common to ``TaskManager`` (cache) and ``TaskService`` (durable).

    Both expose ``update_progress(task_id, step, data)`` (R-01), so the helper
    depends on the behaviour rather than a concrete class.
    """

    def update_progress(self, task_id: str, step: str, data: dict) -> None: ...


def record_degraded_step(
    tm: ProgressSink,
    task_id: str,
    step: str,
    reason: str,
    extra: Optional[dict] = None,
) -> None:
    """Mark a non-critical step as degraded and emit a structured warning.

    Writes ``progress[step] = {"status": "degraded", "reason": reason, **extra}``
    via ``tm.update_progress`` and logs a structured ``warning`` carrying the step
    and reason. This is the handler for an ALREADY-caught failure: it records, it
    does NOT re-raise (CT1, BR1).

    Args:
        tm: A progress sink (``TaskService`` durable or ``TaskManager`` cache).
        task_id: The task whose step is being degraded.
        step: The step name (e.g. ``"prizes"``, ``"phantoms"``).
        reason: A human-readable failure reason (usually ``str(exc)``).
        extra: Optional additional fields merged into the step payload (e.g.
            zeroed counters so downstream readers see a well-formed shape).
    """
    payload = {"status": StepStatus.DEGRADED, "reason": reason}
    if extra:
        payload.update(extra)
    tm.update_progress(task_id, step, payload)
    logger.warning(
        "sync step degraded",
        extra={"sync_step": step, "reason": reason},
    )
