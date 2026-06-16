import pytest

from app.services.exceptions import ProjectConflict, ProjectNotFound
from app.services.project_service import ProjectService
from tests.factories import ProjectFactory, TaskFactory
from tests.fakes import FakeRepository


def make_service(projects=None):
    return ProjectService(FakeRepository(projects or []))


# --- get_project ---


def test_get_project_returns_project():
    project = ProjectFactory(waiting=True)
    service = make_service([project])

    result = service.get_project(project.id)

    assert result.id == project.id


def test_get_project_raises_not_found():
    service = make_service()

    with pytest.raises(ProjectNotFound):
        service.get_project(ProjectFactory().id)


# --- create_project ---


def test_create_project_returns_project_with_name():
    service = make_service()

    result = service.create_project("New Project")

    assert result.name == "New Project"


# --- delete_project ---


def test_delete_project_removes_waiting_project():
    project = ProjectFactory(waiting=True)
    repo = FakeRepository([project])
    service = ProjectService(repo)

    service.delete_project(project.id)

    assert repo.get_project(project.id) is None


def test_delete_in_progress_project_raises_conflict():
    project = ProjectFactory(in_progress=True)
    service = make_service([project])

    with pytest.raises(ProjectConflict):
        service.delete_project(project.id)


# --- start_project ---


def test_start_project_transitions_to_in_progress():
    project = ProjectFactory(waiting=True)
    service = make_service([project])

    result = service.start_project(project.id)

    assert result.is_active is True


def test_start_non_waiting_project_raises_conflict():
    project = ProjectFactory(in_progress=True)
    service = make_service([project])

    with pytest.raises(ProjectConflict):
        service.start_project(project.id)


# --- finish_project ---


def test_finish_project_transitions_to_done():
    project = ProjectFactory(in_progress=True)
    task = TaskFactory(done=True, project_id=project.id)
    project.tasks = [task]
    service = make_service([project])

    result = service.finish_project(project.id)

    assert result.status.value == "DONE"


def test_finish_project_with_pending_tasks_raises_conflict():
    project = ProjectFactory(in_progress=True)
    project.tasks = [TaskFactory(pending=True, project_id=project.id)]
    service = make_service([project])

    with pytest.raises(ProjectConflict):
        service.finish_project(project.id)


def test_finish_project_with_no_tasks_raises_conflict():
    project = ProjectFactory(in_progress=True)
    service = make_service([project])

    with pytest.raises(ProjectConflict):
        service.finish_project(project.id)


def test_finish_non_active_project_raises_conflict():
    project = ProjectFactory(waiting=True)
    service = make_service([project])

    with pytest.raises(ProjectConflict):
        service.finish_project(project.id)


# --- cancel_project ---


def test_cancel_project_transitions_to_cancelled():
    project = ProjectFactory(waiting=True)
    service = make_service([project])

    result = service.cancel_project(project.id)

    assert result.status.value == "CANCELLED"


def test_cancel_done_project_raises_conflict():
    project = ProjectFactory(done=True)
    service = make_service([project])

    with pytest.raises(ProjectConflict):
        service.cancel_project(project.id)
