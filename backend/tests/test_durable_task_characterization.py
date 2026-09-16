"""Characterization tests for the CURRENT ``TaskManager`` behavior (Step 3).

These are a safety net, NOT TDD: they must pass against TODAY's in-memory
``TaskManager`` BEFORE the durability refactor, freezing the observable
behavior — including the known failure modes the durability work will fix
(C5: characterize ``TaskManager`` before refactoring).

Frozen behaviors:
* A sync task lives only in process memory, so a "restart" (a fresh
  ``TaskManager``) loses it entirely (the FR1.4 gap).
* ``get_active_task`` marks a task stale after 600s (10 minutes) and stops
  reporting it as active (the in-memory staleness heuristic).
* ``create_task`` caps the store at 20 tasks, evicting the oldest (the memory
  cap that silently drops history).

No database and no network are touched: ``TaskManager`` is pure in-memory.
"""

from datetime import datetime, timedelta

from app.services.task_manager import TaskManager, TaskStatus


def test_in_memory_task_is_lost_after_restart():
    """A task created in one manager is absent from a fresh one (restart gap)."""
    manager = TaskManager()
    task = manager.create_task("all", "champ-1")
    assert manager.get_task(task.task_id) is not None

    # Simulate a process restart: a brand-new manager has no memory of it.
    restarted = TaskManager()
    assert restarted.get_task(task.task_id) is None


def test_get_active_task_returns_pending_task():
    """A freshly created (pending) task is reported as active for its champ."""
    manager = TaskManager()
    task = manager.create_task("all", "champ-1")
    active = manager.get_active_task("champ-1")
    assert active is not None
    assert active.task_id == task.task_id
    assert active.status == TaskStatus.PENDING


def test_get_active_task_filters_by_championship():
    """An active task for one championship is not returned for another."""
    manager = TaskManager()
    manager.create_task("all", "champ-1")
    assert manager.get_active_task("champ-2") is None


def test_get_active_task_marks_stale_after_600s():
    """A task older than 10 minutes is marked FAILED and no longer active."""
    manager = TaskManager()
    task = manager.create_task("all", "champ-1")
    # Backdate creation just past the 600s staleness threshold.
    task.created_at = datetime.now() - timedelta(seconds=601)

    active = manager.get_active_task("champ-1")
    assert active is None
    assert task.status == TaskStatus.FAILED
    assert task.error == "Task timed out (>10 min)"
    assert task.completed_at is not None


def test_get_active_task_keeps_task_just_under_600s():
    """A task younger than the threshold stays active (boundary check)."""
    manager = TaskManager()
    task = manager.create_task("all", "champ-1")
    task.created_at = datetime.now() - timedelta(seconds=599)

    active = manager.get_active_task("champ-1")
    assert active is not None
    assert active.task_id == task.task_id
    assert active.status == TaskStatus.PENDING


def test_create_task_caps_store_at_20():
    """Creating more than 20 tasks caps the store at 20, evicting the oldest.

    Eviction runs inside ``create_task`` and drops the task with the smallest
    ``created_at`` at that moment. The first task is backdated well into the
    past so it is the unambiguous oldest and is the one evicted once the cap is
    exceeded, freezing the "silently drops history" behavior.
    """
    manager = TaskManager()
    first = manager.create_task("all", "champ-0")
    # Force the first task to be the unambiguous oldest before the cap trips.
    first.created_at = datetime.now() - timedelta(hours=1)

    for index in range(1, 25):
        manager.create_task("all", f"champ-{index}")

    # The store never grows beyond the hard cap of 20.
    assert len(manager._tasks) == 20
    # The unambiguous oldest task was evicted (history silently dropped).
    assert manager.get_task(first.task_id) is None


def test_mark_completed_sets_result_and_clears_step():
    """Completing a task freezes its terminal state (current in-memory shape)."""
    manager = TaskManager()
    task = manager.create_task("all", "champ-1")
    manager.mark_running(task.task_id, step="players")
    manager.mark_completed(task.task_id, {"players": {"records_synced": 3}})

    stored = manager.get_task(task.task_id)
    assert stored.status == TaskStatus.COMPLETED
    assert stored.result == {"players": {"records_synced": 3}}
    assert stored.current_step is None
    assert stored.completed_at is not None
