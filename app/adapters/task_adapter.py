from app.adapters.datetime_adapter import to_aware, to_naive
from app.domain.task import Priority, Task, TaskStatus
from app.ports.task_wire import TaskResponse
from app.repository.models import TaskModel


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
        created_at=to_naive(task.created_at),
        completed_at=to_naive(task.completed_at),
    )


def from_model(model: TaskModel) -> Task:
    return Task(
        id=model.id,
        project_id=model.project_id,
        title=model.title,
        status=TaskStatus(model.status),
        priority=Priority(model.priority),
        created_at=to_aware(model.created_at),
        completed_at=to_aware(model.completed_at),
    )
