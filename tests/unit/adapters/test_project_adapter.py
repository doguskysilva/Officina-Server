from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.adapters.project_adapter import (
    from_create_request,
    from_model,
    record_to_response,
    to_model,
)
from app.domain.project import Project, ProjectStatus
from app.domain.task import Priority, Task, TaskStatus
from app.ports.project_wire import ProjectCreate
from app.repository.models import ProjectModel, TaskModel

PROJECT_ID = uuid4()
TASK_ID = uuid4()
NOW = datetime(2026, 6, 4, 12, 0, tzinfo=UTC)
COMPLETED = datetime(2026, 6, 5, 10, 0, tzinfo=UTC)


def _make_project(**kwargs) -> Project:
    defaults = dict(id=PROJECT_ID, name="My Project", status=ProjectStatus.WAITING, created_at=NOW)
    return Project(**{**defaults, **kwargs})


def _make_task(**kwargs) -> Task:
    defaults = dict(
        id=uuid4(),
        project_id=PROJECT_ID,
        title="Task",
        status=TaskStatus.PENDING,
        priority=Priority.MEDIUM,
        created_at=NOW,
    )
    return Task(**{**defaults, **kwargs})


def _make_model(tasks: list[TaskModel] | None = None, **kwargs) -> ProjectModel:
    defaults = dict(
        id=PROJECT_ID,
        name="My Project",
        status="WAITING",
        created_at=NOW.replace(tzinfo=None),
    )
    model = ProjectModel(**{**defaults, **kwargs})
    model.tasks = tasks or []
    return model


def _make_task_model(**kwargs) -> TaskModel:
    defaults = dict(
        id=TASK_ID,
        project_id=PROJECT_ID,
        title="Task",
        status="PENDING",
        priority="MEDIUM",
        created_at=NOW.replace(tzinfo=None),
    )
    return TaskModel(**{**defaults, **kwargs})


# --- from_create_request ---


def test_from_create_request_extracts_name():
    body = ProjectCreate(name="Officina App")

    result = from_create_request(body)

    assert result == "Officina App"


# --- record_to_response ---


def test_record_to_response_maps_all_fields():
    project = _make_project(id=PROJECT_ID)

    response = record_to_response(project)

    assert response.id == PROJECT_ID
    assert response.name == "My Project"
    assert response.status == ProjectStatus.WAITING
    assert response.created_at == NOW
    assert response.completed_at is None


def test_record_to_response_no_tasks_computes_defaults():
    response = record_to_response(_make_project())

    assert response.tasks == []
    assert response.pending_count == 0
    assert response.can_finish is False
    assert response.is_active is False


def test_record_to_response_in_progress_is_active():
    response = record_to_response(_make_project(status=ProjectStatus.IN_PROGRESS))

    assert response.is_active is True


def test_record_to_response_maps_completed_at():
    response = record_to_response(_make_project(status=ProjectStatus.DONE, completed_at=COMPLETED))

    assert response.status == ProjectStatus.DONE
    assert response.completed_at == COMPLETED


@pytest.mark.parametrize("n_pending,n_done", [(2, 1), (1, 0), (3, 3)])
def test_record_to_response_pending_count(n_pending, n_done):
    tasks = [_make_task(status=TaskStatus.PENDING) for _ in range(n_pending)]
    tasks += [_make_task(status=TaskStatus.DONE) for _ in range(n_done)]
    response = record_to_response(_make_project(status=ProjectStatus.IN_PROGRESS, tasks=tasks))

    assert response.pending_count == n_pending


def test_record_to_response_can_finish_when_all_tasks_done():
    tasks = [_make_task(status=TaskStatus.DONE) for _ in range(3)]
    response = record_to_response(_make_project(status=ProjectStatus.IN_PROGRESS, tasks=tasks))

    assert response.can_finish is True
    assert response.pending_count == 0


def test_record_to_response_cannot_finish_with_pending_tasks():
    tasks = [_make_task(status=TaskStatus.DONE), _make_task(status=TaskStatus.PENDING)]
    response = record_to_response(_make_project(status=ProjectStatus.IN_PROGRESS, tasks=tasks))

    assert response.can_finish is False


# --- to_model ---


def test_to_model_maps_id():
    model = to_model(_make_project())

    assert model.id == PROJECT_ID


def test_to_model_maps_name_and_status():
    model = to_model(_make_project())

    assert model.name == "My Project"
    assert model.status == "WAITING"


def test_to_model_strips_timezone():
    model = to_model(_make_project())

    assert model.created_at.tzinfo is None


def test_to_model_completed_at_none():
    model = to_model(_make_project())

    assert model.completed_at is None


def test_to_model_does_not_include_tasks():
    project = _make_project(tasks=[_make_task()])

    model = to_model(project)

    assert model.tasks == []


# --- from_model ---


def test_from_model_maps_id():
    project = from_model(_make_model())

    assert project.id == PROJECT_ID


def test_from_model_maps_name_and_status():
    project = from_model(_make_model())

    assert project.name == "My Project"
    assert project.status == ProjectStatus.WAITING


def test_from_model_attaches_utc_to_created_at():
    project = from_model(_make_model())

    assert project.created_at.tzinfo is UTC


def test_from_model_completed_at_none():
    project = from_model(_make_model())

    assert project.completed_at is None


def test_from_model_attaches_utc_to_completed_at():
    model = _make_model(status="DONE", completed_at=COMPLETED.replace(tzinfo=None))

    project = from_model(model)

    assert project.completed_at is not None
    assert project.completed_at.tzinfo is UTC


def test_from_model_empty_tasks():
    project = from_model(_make_model())

    assert project.tasks == []


def test_from_model_maps_embedded_tasks():
    project = from_model(_make_model(tasks=[_make_task_model()]))

    assert len(project.tasks) == 1
    assert project.tasks[0].id == TASK_ID
    assert project.tasks[0].status == TaskStatus.PENDING


def test_from_model_reconstructs_all_project_statuses():
    for status in ("WAITING", "IN_PROGRESS", "DONE", "CANCELLED"):
        project = from_model(_make_model(status=status))
        assert project.status == ProjectStatus(status)
