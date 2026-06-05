from datetime import UTC, datetime
from uuid import uuid4

from app.adapters.task_adapter import record_to_response
from app.domain.task import Priority, Task, TaskStatus

NOW = datetime(2026, 6, 4, 12, 0, tzinfo=UTC)
COMPLETED_AT = datetime(2026, 6, 4, 14, 0, tzinfo=UTC)


def test_maps_all_fields():
    task_id = uuid4()
    project_id = uuid4()
    task = Task(
        id=task_id,
        project_id=project_id,
        title="Write tests",
        status=TaskStatus.PENDING,
        priority=Priority.HIGH,
        created_at=NOW,
    )

    response = record_to_response(task)

    assert response.id == task_id
    assert response.project_id == project_id
    assert response.title == "Write tests"
    assert response.status == TaskStatus.PENDING
    assert response.priority == Priority.HIGH
    assert response.created_at == NOW
    assert response.completed_at is None


def test_maps_completed_at():
    task = Task(
        id=uuid4(),
        project_id=uuid4(),
        title="Done task",
        status=TaskStatus.DONE,
        priority=Priority.LOW,
        created_at=NOW,
        completed_at=COMPLETED_AT,
    )

    response = record_to_response(task)

    assert response.status == TaskStatus.DONE
    assert response.completed_at == COMPLETED_AT


def test_maps_cancelled_status():
    task = Task(
        id=uuid4(),
        project_id=uuid4(),
        title="Dropped",
        status=TaskStatus.CANCELLED,
        priority=Priority.MEDIUM,
        created_at=NOW,
    )

    response = record_to_response(task)

    assert response.status == TaskStatus.CANCELLED
