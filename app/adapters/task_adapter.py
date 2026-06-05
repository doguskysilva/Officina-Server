from app.domain.task import Task
from app.ports.task_wire import TaskResponse


def record_to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        title=task.title,
        status=task.status,
        priority=task.priority,
        created_at=task.created_at,
        completed_at=task.completed_at,
    )
