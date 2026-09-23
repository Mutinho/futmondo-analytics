"""Tests de caracterización del comportamiento degradado de pasos de sync
(FR3.1.2 / BR1 / BR2).

Caracterizan cómo `sync.py` escribe el progreso de los pasos NO críticos
(`prizes`, `phantoms`) usando un fake del task manager (dict en memoria):
- Un paso que lanza queda `status="degraded"` con `reason` (NUNCA `done`).
- Un paso que NO lanza conserva `status="done"` (sin regresión, BR2).

Se ejercita el helper `record_degraded_step` a nivel de unidad reproduciendo la
forma exacta del payload que `sync.py` escribe en las ramas `except` de `prizes`
y `phantoms`, sin ejecutar `_run_sync_in_background` (sin red ni BD).
"""

import pytest

from app.services.sync_step_status import record_degraded_step
from app.services.task_manager import TaskManager, TaskStatus


@pytest.fixture
def task_manager():
    """A real in-memory TaskManager (no network, no DB)."""
    return TaskManager()


def _new_task(tm: TaskManager):
    return tm.create_task("full", "champ-1")


def test_prizes_step_that_raises_is_degraded_not_done(task_manager):
    task = _new_task(task_manager)

    # Simulate sync.py's prizes `except` branch payload shape.
    try:
        raise RuntimeError("prizes failed upstream")
    except Exception as pr_err:
        record_degraded_step(
            task_manager, task.task_id, "prizes", str(pr_err), {"records_synced": 0}
        )

    step = task.progress["prizes"]
    assert step["status"] == "degraded"
    assert step["status"] != "done"
    assert step["reason"] == "prizes failed upstream"
    assert step["records_synced"] == 0


def test_phantoms_step_that_raises_is_degraded_not_done(task_manager):
    task = _new_task(task_manager)

    try:
        raise ValueError("phantoms check exploded")
    except Exception as ph_err:
        record_degraded_step(
            task_manager, task.task_id, "phantoms", str(ph_err), {"total_phantoms": 0}
        )

    step = task.progress["phantoms"]
    assert step["status"] == "degraded"
    assert step["reason"] == "phantoms check exploded"
    assert step["total_phantoms"] == 0


def test_step_that_does_not_raise_keeps_done(task_manager):
    task = _new_task(task_manager)

    # Happy path: sync.py writes {"status": "done", **result} (BR2). No regression.
    task_manager.update_progress(
        task.task_id, "prizes", {"status": "done", "records_synced": 42}
    )

    step = task.progress["prizes"]
    assert step["status"] == "done"
    assert "reason" not in step
    assert step["records_synced"] == 42


def test_degraded_step_does_not_fail_the_task(task_manager):
    """A degraded non-critical step does not, by itself, fail the whole task."""
    task = _new_task(task_manager)

    record_degraded_step(task_manager, task.task_id, "prizes", "boom", {"records_synced": 0})

    # The helper only touches progress; task-level status is unaffected here.
    assert task.status != TaskStatus.FAILED
    assert task.progress["prizes"]["status"] == "degraded"
