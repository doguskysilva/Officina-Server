import pytest

from app.adapters.project_adapter import (
    from_model,
    from_request,
    to_list_response,
    to_model,
    to_response,
)
from app.domain.project import ProjectStatus, ProjectSummary
from app.domain.task import TaskStatus
from app.ports.project_wire import ProjectCreate
from tests.factories import ProjectFactory, ProjectModelFactory, TaskFactory, TaskModelFactory

# --- from_request ---


def test_from_request_extracts_name():
    body = ProjectCreate(name="Officina App")

    result = from_request(body)

    assert result == "Officina App"


# --- to_response ---


def test_to_response_maps_all_fields():
    project = ProjectFactory()

    response = to_response(project)

    assert response.id == project.id
    assert response.name == project.name
    assert response.status == project.status
    assert response.created_at == project.created_at
    assert response.completed_at is None


def test_to_response_no_tasks_computes_defaults():
    response = to_response(ProjectFactory(waiting=True))

    assert response.tasks == []
    assert response.pending_count == 0
    assert response.can_finish is False
    assert response.is_active is False


def test_to_response_in_progress_is_active():
    response = to_response(ProjectFactory(in_progress=True))

    assert response.is_active is True


def test_to_response_maps_completed_at():
    project = ProjectFactory(done=True)

    response = to_response(project)

    assert response.status == ProjectStatus.DONE
    assert response.completed_at == project.completed_at


@pytest.mark.parametrize("n_pending,n_done", [(2, 1), (1, 0), (3, 3)])
def test_to_response_pending_count(n_pending, n_done):
    tasks = [TaskFactory(pending=True) for _ in range(n_pending)]
    tasks += [TaskFactory(done=True) for _ in range(n_done)]
    project = ProjectFactory(in_progress=True, tasks=tasks)

    response = to_response(project)

    assert response.pending_count == n_pending


def test_to_response_can_finish_when_all_tasks_done():
    tasks = [TaskFactory(done=True) for _ in range(3)]
    response = to_response(ProjectFactory(in_progress=True, tasks=tasks))

    assert response.can_finish is True
    assert response.pending_count == 0


def test_to_response_cannot_finish_with_pending_tasks():
    tasks = [TaskFactory(done=True), TaskFactory(pending=True)]
    response = to_response(ProjectFactory(in_progress=True, tasks=tasks))

    assert response.can_finish is False


def test_to_list_response_maps_all_fields():
    project = ProjectFactory()
    summary = ProjectSummary(
        id=project.id,
        name="API Rewrite",
        status=ProjectStatus.IN_PROGRESS,
        created_at=project.created_at,
        completed_at=None,
        pending_count=3,
        can_finish=False,
        is_active=True,
    )

    response = to_list_response(summary)

    assert response.id == summary.id
    assert response.name == summary.name
    assert response.status == summary.status
    assert response.pending_count == summary.pending_count
    assert response.can_finish == summary.can_finish
    assert response.is_active == summary.is_active


# --- to_model ---


def test_to_model_maps_id():
    project = ProjectFactory()

    assert to_model(project).id == project.id


def test_to_model_maps_name_and_status():
    project = ProjectFactory()
    model = to_model(project)

    assert model.name == project.name
    assert model.status == project.status


def test_to_model_strips_timezone():
    model = to_model(ProjectFactory())

    assert model.created_at.tzinfo is None


def test_to_model_completed_at_none():
    assert to_model(ProjectFactory()).completed_at is None


def test_to_model_does_not_include_tasks():
    project = ProjectFactory(in_progress=True, tasks=[TaskFactory()])

    assert to_model(project).tasks == []


# --- from_model ---


def test_from_model_maps_id():
    model = ProjectModelFactory()

    assert from_model(model).id == model.id


def test_from_model_maps_name_and_status():
    model = ProjectModelFactory()
    project = from_model(model)

    assert project.name == model.name
    assert project.status == ProjectStatus(model.status)


def test_from_model_attaches_utc_to_created_at():
    from datetime import UTC

    project = from_model(ProjectModelFactory())

    assert project.created_at.tzinfo is UTC


def test_from_model_completed_at_none():
    assert from_model(ProjectModelFactory()).completed_at is None


def test_from_model_attaches_utc_to_completed_at():
    from datetime import UTC

    model = ProjectModelFactory(done=True)
    project = from_model(model)

    assert project.completed_at is not None
    assert project.completed_at.tzinfo is UTC


def test_from_model_empty_tasks():
    assert from_model(ProjectModelFactory()).tasks == []


def test_from_model_maps_embedded_tasks():
    task_model = TaskModelFactory(pending=True)
    project = from_model(ProjectModelFactory(tasks=[task_model]))

    assert len(project.tasks) == 1
    assert project.tasks[0].id == task_model.id
    assert project.tasks[0].status == TaskStatus.PENDING


def test_from_model_reconstructs_all_project_statuses():
    for status in ("WAITING", "IN_PROGRESS", "DONE", "CANCELLED"):
        project = from_model(ProjectModelFactory(status=status))
        assert project.status == ProjectStatus(status)
