from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.adapters.project_adapter import from_create_request, record_to_response
from app.domain.project import Project, ProjectStatus
from app.domain.task import Priority, Task, TaskStatus
from app.ports.project_wire import ProjectCreate

NOW = datetime(2026, 6, 4, 12, 0, tzinfo=UTC)
COMPLETED_AT = datetime(2026, 6, 5, 10, 0, tzinfo=UTC)


def _make_project(**kwargs) -> Project:
    defaults = dict(id=uuid4(), name="My Project", status=ProjectStatus.WAITING, created_at=NOW)
    return Project(**{**defaults, **kwargs})


def _make_task(**kwargs) -> Task:
    defaults = dict(
        id=uuid4(),
        project_id=uuid4(),
        title="Task",
        status=TaskStatus.PENDING,
        priority=Priority.MEDIUM,
        created_at=NOW,
    )
    return Task(**{**defaults, **kwargs})


# --- from_create_request ---


def test_from_create_request_extracts_name():
    body = ProjectCreate(name="Officina App")

    result = from_create_request(body)

    assert result == "Officina App"


# --- record_to_response ---


def test_record_to_response_maps_all_fields():
    project_id = uuid4()
    project = _make_project(id=project_id)

    response = record_to_response(project)

    assert response.id == project_id
    assert response.name == "My Project"
    assert response.status == ProjectStatus.WAITING
    assert response.created_at == NOW
    assert response.completed_at is None


def test_record_to_response_no_tasks_computes_defaults():
    project = _make_project()

    response = record_to_response(project)

    assert response.tasks == []
    assert response.pending_count == 0
    assert response.can_finish is False
    assert response.is_active is False


def test_record_to_response_in_progress_is_active():
    project = _make_project(status=ProjectStatus.IN_PROGRESS)

    response = record_to_response(project)

    assert response.is_active is True


def test_record_to_response_maps_completed_at():
    project = _make_project(status=ProjectStatus.DONE, completed_at=COMPLETED_AT)

    response = record_to_response(project)

    assert response.status == ProjectStatus.DONE
    assert response.completed_at == COMPLETED_AT


@pytest.mark.parametrize("n_pending,n_done", [(2, 1), (1, 0), (3, 3)])
def test_record_to_response_pending_count(n_pending, n_done):
    tasks = [_make_task(status=TaskStatus.PENDING) for _ in range(n_pending)]
    tasks += [_make_task(status=TaskStatus.DONE) for _ in range(n_done)]
    project = _make_project(status=ProjectStatus.IN_PROGRESS, tasks=tasks)

    response = record_to_response(project)

    assert response.pending_count == n_pending


def test_record_to_response_can_finish_when_all_tasks_done():
    tasks = [_make_task(status=TaskStatus.DONE) for _ in range(3)]
    project = _make_project(status=ProjectStatus.IN_PROGRESS, tasks=tasks)

    response = record_to_response(project)

    assert response.can_finish is True
    assert response.pending_count == 0


def test_record_to_response_cannot_finish_with_pending_tasks():
    tasks = [_make_task(status=TaskStatus.DONE), _make_task(status=TaskStatus.PENDING)]
    project = _make_project(status=ProjectStatus.IN_PROGRESS, tasks=tasks)

    response = record_to_response(project)

    assert response.can_finish is False
