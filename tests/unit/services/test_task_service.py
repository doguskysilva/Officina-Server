import pytest

from app.domain.task import Priority, TaskStatus
from app.services.exceptions import ProjectConflict, ProjectNotFound
from app.services.task_service import TaskService
from tests.factories import ProjectFactory, TaskFactory
from tests.fakes import FakeRepository


def make_service(projects=None):
    return TaskService(FakeRepository(projects or []))


# --- add_task ---


def test_add_task_appends_task_to_project():
    project = ProjectFactory(in_progress=True)
    service = make_service([project])

    task = service.add_task(project.id, "Write docs", Priority.HIGH)

    assert task.title == "Write docs"
    assert task.priority == Priority.HIGH
    assert task.status == TaskStatus.PENDING


def test_add_task_to_non_active_project_raises_conflict():
    project = ProjectFactory(waiting=True)
    service = make_service([project])

    with pytest.raises(ProjectConflict):
        service.add_task(project.id, "Task", Priority.LOW)


def test_add_task_to_missing_project_raises_not_found():
    service = make_service()

    with pytest.raises(ProjectNotFound):
        service.add_task(ProjectFactory().id, "Task", Priority.LOW)


# --- complete_tasks ---


def test_complete_tasks_marks_tasks_done():
    project = ProjectFactory(in_progress=True)
    task = TaskFactory(pending=True, project_id=project.id)
    project.tasks = [task]
    service = make_service([project])

    result = service.complete_tasks(project.id, {task.id})

    assert result.tasks[0].status == TaskStatus.DONE


def test_complete_tasks_on_non_active_project_raises_conflict():
    project = ProjectFactory(waiting=True)
    service = make_service([project])

    with pytest.raises(ProjectConflict):
        service.complete_tasks(project.id, set())


# --- cancel_tasks ---


def test_cancel_tasks_marks_tasks_cancelled():
    project = ProjectFactory(in_progress=True)
    task = TaskFactory(pending=True, project_id=project.id)
    project.tasks = [task]
    service = make_service([project])

    result = service.cancel_tasks(project.id, {task.id})

    assert result.tasks[0].status == TaskStatus.CANCELLED


def test_cancel_tasks_on_non_active_project_raises_conflict():
    project = ProjectFactory(waiting=True)
    service = make_service([project])

    with pytest.raises(ProjectConflict):
        service.cancel_tasks(project.id, set())


# --- complete_all_tasks ---


def test_complete_all_tasks_marks_all_pending_done():
    project = ProjectFactory(in_progress=True)
    project.tasks = [TaskFactory(pending=True, project_id=project.id) for _ in range(3)]
    service = make_service([project])

    result = service.complete_all_tasks(project.id)

    assert all(t.status == TaskStatus.DONE for t in result.tasks)


def test_complete_all_tasks_on_non_active_project_raises_conflict():
    project = ProjectFactory(waiting=True)
    service = make_service([project])

    with pytest.raises(ProjectConflict):
        service.complete_all_tasks(project.id)


# --- remove_tasks ---


def test_remove_tasks_removes_specified_tasks():
    project = ProjectFactory(in_progress=True)
    task = TaskFactory(project_id=project.id)
    project.tasks = [task]
    service = make_service([project])

    result = service.remove_tasks(project.id, {task.id})

    assert result.tasks == []


def test_remove_tasks_on_non_active_project_raises_conflict():
    project = ProjectFactory(waiting=True)
    service = make_service([project])

    with pytest.raises(ProjectConflict):
        service.remove_tasks(project.id, set())
