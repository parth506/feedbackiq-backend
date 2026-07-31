"""
In-memory Task Queue — development stub implementing TaskQueueInterface.

Stores tasks in a process-scoped dict.
Replace with CeleryTaskQueue or RedisQueueTaskQueue in production.
"""
import logging
import uuid
from typing import Any, Dict

from app.core.interfaces import TaskQueueInterface

logger = logging.getLogger(__name__)

_task_store: Dict[str, Dict[str, Any]] = {}


class InMemoryTaskQueue(TaskQueueInterface):
    """
    Simple in-memory task queue for local development.
    Tasks are not persisted and not executed — they are stored for inspection.
    """

    async def enqueue(self, task_name: str, payload: Dict[str, Any]) -> str:
        task_id = str(uuid.uuid4())
        _task_store[task_id] = {
            "task_id": task_id,
            "task_name": task_name,
            "payload": payload,
            "status": "queued",
        }
        logger.info("Task enqueued: %s (id=%s)", task_name, task_id)
        return task_id

    async def get_status(self, task_id: str) -> Dict[str, Any]:
        return _task_store.get(task_id, {"task_id": task_id, "status": "not_found"})
