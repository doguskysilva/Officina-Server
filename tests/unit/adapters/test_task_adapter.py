from datetime import UTC, datetime
from uuid import uuid4

from app.adapters.task_adapter import from_model, record_to_response, to_model
from app.domain.task import Priority, Task, TaskStatus
from app.repository.models import TaskModel

TASK_ID = uuid4()
PROJECT_ID = uuid4()
NOW = datetime(2026, 6, 4, 12, 0, tzinfo=UTC)
COMPLETED = datetime(2026, 6, 4, 14, 0, tzinfo=UTC)


def _make_task(**kwargs) -> Task:
    defaults = dict(
        id=TASK_ID,
        project_id=PROJECT_ID,
        title="Write tests",
        status=TaskStatus.PENDING,
        priority=Priority.HIGH,
        created_at=NOW,
    )
    return Task(**{**defaults, **kwargs})


def _make_model(**kwargs) -> TaskModel:
    defaults = dict(
        id=TASK_ID,
        project_id=PROJECT_ID,
        title="Write tests",
        status="PENDING",
        priority="HIGH",
        created_at=NOW.replace(tzinfo=None),
    )
    return TaskModel(**{**defaults, **kwargs})


# --- record_to_response ---


def test_record_to_response_maps_all_fields():
    task = _make_task()

    response = record_to_response(task)

    assert response.id == TASK_ID
    assert response.project_id == PROJECT_ID
    assert response.title == "Write tests"
    assert response.status == TaskStatus.PENDING
    assert response.priority == Priority.HIGH
    assert response.created_at == NOW
    assert response.completed_at is None


def test_record_to_response_maps_completed_at():
    task = _make_task(status=TaskStatus.DONE, completed_at=COMPLETED)

    response = record_to_response(task)

    assert response.status == TaskStatus.DONE
    assert response.completed_at == COMPLETED


def test_record_to_response_maps_cancelled_status():
    task = _make_task(status=TaskStatus.CANCELLED)

    response = record_to_response(task)

    assert response.status == TaskStatus.CANCELLED


# --- to_model ---


def test_to_model_maps_ids():
    model = to_model(_make_task())

    assert model.id == TASK_ID
    assert model.project_id == PROJECT_ID


def test_to_model_maps_title_and_enums():
    model = to_model(_make_task())

    assert model.title == "Write tests"
    assert model.status == "PENDING"
    assert model.priority == "HIGH"


def test_to_model_strips_timezone():
    model = to_model(_make_task())

    assert model.created_at.tzinfo is None


def test_to_model_completed_at_none():
    model = to_model(_make_task())

    assert model.completed_at is None


def test_to_model_strips_timezone_from_completed_at():
    model = to_model(_make_task(status=TaskStatus.DONE, completed_at=COMPLETED))

    assert model.completed_at is not None
    assert model.completed_at.tzinfo is None


# --- from_model ---


def test_from_model_maps_ids():
    task = from_model(_make_model())

    assert task.id == TASK_ID
    assert task.project_id == PROJECT_ID


def test_from_model_maps_title_and_enums():
    task = from_model(_make_model())

    assert task.title == "Write tests"
    assert task.status == TaskStatus.PENDING
    assert task.priority == Priority.HIGH


def test_from_model_attaches_utc_to_created_at():
    task = from_model(_make_model())

    assert task.created_at.tzinfo is UTC


def test_from_model_completed_at_none():
    task = from_model(_make_model())

    assert task.completed_at is None


def test_from_model_attaches_utc_to_completed_at():
    model = _make_model(status="DONE", completed_at=COMPLETED.replace(tzinfo=None))

    task = from_model(model)

    assert task.completed_at is not None
    assert task.completed_at.tzinfo is UTC


def test_from_model_reconstructs_all_enum_values():
    for status in ("PENDING", "DONE", "CANCELLED"):
        task = from_model(_make_model(status=status))
        assert task.status == TaskStatus(status)

    for priority in ("LOW", "MEDIUM", "HIGH"):
        task = from_model(_make_model(priority=priority))
        assert task.priority == Priority(priority)
