"""Synthetic synchronous worker for teaching; no broker, persistence or backoff."""
from dataclasses import dataclass
from typing import Callable


@dataclass
class Task:
    id: str
    status: str = "queued"
    attempts: int = 0
    result: str | None = None


def run_task(task: Task, handle: Callable[[str], str], max_attempts: int = 2) -> Task:
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")
    while task.attempts < max_attempts:
        task.status = "running"
        task.attempts += 1
        try:
            task.result = handle(task.id)
        except ValueError:
            task.status = "failed"
        else:
            task.status = "done"
            return task
    return task
