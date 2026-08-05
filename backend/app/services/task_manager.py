"""
Background Task Manager — tracks async sync tasks with progress updates.
"""

import uuid
import threading
import logging
from datetime import datetime
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class TaskStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Task:
    def __init__(self, task_id: str, sync_type: str, championship_id: str):
        self.task_id = task_id
        self.sync_type = sync_type
        self.championship_id = championship_id
        self.status = TaskStatus.PENDING
        self.progress: Dict[str, Any] = {}
        self.current_step: Optional[str] = None
        self.result: Optional[Dict] = None
        self.error: Optional[str] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "sync_type": self.sync_type,
            "championship_id": self.championship_id,
            "status": self.status,
            "current_step": self.current_step,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class TaskManager:
    """In-memory task store. Tracks background sync jobs."""

    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._lock = threading.Lock()

    def create_task(self, sync_type: str, championship_id: str) -> Task:
        task_id = uuid.uuid4().hex[:12]
        task = Task(task_id, sync_type, championship_id)
        with self._lock:
            self._tasks[task_id] = task
            # Keep only last 20 tasks to avoid memory leak
            if len(self._tasks) > 20:
                oldest_key = min(self._tasks, key=lambda k: self._tasks[k].created_at)
                del self._tasks[oldest_key]
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        with self._lock:
            return self._tasks.get(task_id)

    def get_active_task(self, championship_id: str = None) -> Optional[Task]:
        """Return the currently running task, optionally filtered by championship.
        Tasks older than 10 minutes are considered stale and ignored."""
        with self._lock:
            now = datetime.now()
            for task in self._tasks.values():
                if task.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
                    # Consider tasks stale after 10 minutes
                    age = (now - task.created_at).total_seconds()
                    if age > 600:
                        task.status = TaskStatus.FAILED
                        task.error = "Task timed out (>10 min)"
                        task.completed_at = now
                        continue
                    if championship_id is None or task.championship_id == championship_id:
                        return task
        return None

    def mark_running(self, task_id: str, step: str = None):
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            if step:
                task.current_step = step

    def update_progress(self, task_id: str, step: str, data: Dict = None):
        task = self.get_task(task_id)
        if task:
            task.current_step = step
            if data:
                task.progress[step] = data

    def mark_completed(self, task_id: str, result: Dict):
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            task.current_step = None

    def mark_failed(self, task_id: str, error: str):
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error = error
            task.current_step = None


# Global singleton
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager
