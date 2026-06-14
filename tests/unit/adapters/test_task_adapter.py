from datetime import UTC

from app.adapters.task_adapter import from_model, to_model, to_response
from app.domain.task import Priority, TaskStatus
from tests.factories import TaskFactory, TaskModelFactory

# --- to_response ---


def test_to_response_maps_all_fields():
    task = TaskFactory()

    response = to_response(task)

    assert response.id == task.id
    assert response.project_id == task.project_id
    assert response.title == task.title
    assert response.status == task.status
    assert response.priority == task.priority
    assert response.created_at == task.created_at
    assert response.completed_at is None


def test_to_response_maps_completed_at():
    task = TaskFactory(done=True)

    response = to_response(task)

    assert response.status == TaskStatus.DONE
    assert response.completed_at == task.completed_at


def test_to_response_maps_cancelled_status():
    response = to_response(TaskFactory(cancelled=True))

    assert response.status == TaskStatus.CANCELLED


# --- to_model ---


def test_to_model_maps_ids():
    task = TaskFactory()
    model = to_model(task)

    assert model.id == task.id
    assert model.project_id == task.project_id


def test_to_model_maps_title_and_enums():
    task = TaskFactory()
    model = to_model(task)

    assert model.title == task.title
    assert model.status == task.status
    assert model.priority == task.priority


def test_to_model_strips_timezone():
    model = to_model(TaskFactory())

    assert model.created_at.tzinfo is None


def test_to_model_completed_at_none():
    assert to_model(TaskFactory()).completed_at is None


def test_to_model_strips_timezone_from_completed_at():
    model = to_model(TaskFactory(done=True))

    assert model.completed_at is not None
    assert model.completed_at.tzinfo is None


# --- from_model ---


def test_from_model_maps_ids():
    model = TaskModelFactory()
    task = from_model(model)

    assert task.id == model.id
    assert task.project_id == model.project_id


def test_from_model_maps_title_and_enums():
    model = TaskModelFactory()
    task = from_model(model)

    assert task.title == model.title
    assert task.status == TaskStatus(model.status)
    assert task.priority == Priority(model.priority)


def test_from_model_attaches_utc_to_created_at():
    task = from_model(TaskModelFactory())

    assert task.created_at.tzinfo is UTC


def test_from_model_completed_at_none():
    assert from_model(TaskModelFactory()).completed_at is None


def test_from_model_attaches_utc_to_completed_at():
    model = TaskModelFactory(done=True)
    task = from_model(model)

    assert task.completed_at is not None
    assert task.completed_at.tzinfo is UTC


def test_from_model_reconstructs_all_enum_values():
    for status in ("PENDING", "DONE", "CANCELLED"):
        task = from_model(TaskModelFactory(status=status))
        assert task.status == TaskStatus(status)

    for priority in ("LOW", "MEDIUM", "HIGH"):
        task = from_model(TaskModelFactory(priority=priority))
        assert task.priority == Priority(priority)
