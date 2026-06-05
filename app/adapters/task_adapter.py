from datetime import UTC, datetime

from app.domain.task import Priority, Task, TaskStatus
from app.ports.task_wire import TaskResponse
from app.repository.models import TaskModel


def _naive(dt: datetime | None) -> datetime | None:
    return dt.replace(tzinfo=None) if dt is not None else None


def _aware(dt: datetime | None) -> datetime | None:
    return dt.replace(tzinfo=UTC) if dt is not None else None


def to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        title=task.title,
        status=task.status,
        priority=task.priority,
        created_at=task.created_at,
        completed_at=task.completed_at,
    )


def to_model(task: Task) -> TaskModel:
    return TaskModel(
        id=task.id,
        project_id=task.project_id,
        title=task.title,
        status=task.status.value,
        priority=task.priority.value,
        created_at=_naive(task.created_at),
        completed_at=_naive(task.completed_at),
    )


def from_model(model: TaskModel) -> Task:
    return Task(
        id=model.id,
        project_id=model.project_id,
        title=model.title,
        status=TaskStatus(model.status),
        priority=Priority(model.priority),
        created_at=_aware(model.created_at),
        completed_at=_aware(model.completed_at),
    )
