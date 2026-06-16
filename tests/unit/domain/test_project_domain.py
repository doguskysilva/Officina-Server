from uuid import uuid4

import pytest

from app.domain.exceptions import InvalidProjectOperation
from app.domain.project import Project, ProjectStatus
from app.domain.task import Priority, TaskStatus
from tests.factories import ProjectFactory, TaskFactory

# --- create() ---


def test_create_builds_waiting_project():
    project = Project.create("New Project")

    assert project.name == "New Project"
    assert project.status == ProjectStatus.WAITING
    assert project.tasks == []
    assert project.created_at.tzinfo is not None

# --- start() ---


def test_start_sets_status_to_in_progress():
    project = ProjectFactory(waiting=True)

    project.start()

    assert project.status == ProjectStatus.IN_PROGRESS


def test_start_makes_project_active():
    project = ProjectFactory(waiting=True)

    project.start()

    assert project.is_active is True


def test_start_disables_can_start():
    project = ProjectFactory(waiting=True)

    project.start()

    assert project.can_start is False


def test_start_requires_waiting_project():
    project = ProjectFactory(done=True)

    with pytest.raises(InvalidProjectOperation):
        project.start()


# --- cancel() ---


def test_cancel_sets_status_to_cancelled():
    project = ProjectFactory(waiting=True)

    project.cancel()

    assert project.status == ProjectStatus.CANCELLED


def test_cancel_from_in_progress():
    project = ProjectFactory(in_progress=True)

    project.cancel()

    assert project.status == ProjectStatus.CANCELLED
    assert project.is_active is False


def test_cancel_done_project_raises():
    project = ProjectFactory(done=True)

    with pytest.raises(InvalidProjectOperation):
        project.cancel()


# --- complete() ---


def test_complete_sets_status_to_done():
    project = ProjectFactory(in_progress=True)
    project.tasks = [TaskFactory(done=True, project_id=project.id)]

    project.complete()

    assert project.status == ProjectStatus.DONE


def test_complete_sets_completed_at():
    project = ProjectFactory(in_progress=True)
    project.tasks = [TaskFactory(done=True, project_id=project.id)]

    project.complete()

    assert project.completed_at is not None
    assert project.completed_at.tzinfo is not None


def test_complete_completed_at_is_after_created_at():
    project = ProjectFactory(in_progress=True)
    project.tasks = [TaskFactory(done=True, project_id=project.id)]

    project.complete()

    assert project.completed_at > project.created_at


def test_complete_updates_can_finish_derived_state():
    tasks = [TaskFactory(done=True)]
    project = ProjectFactory(in_progress=True, tasks=tasks)

    project.complete()

    assert project.status == ProjectStatus.DONE
    assert not project.is_active
    assert not project.can_cancel


def test_complete_requires_active_project():
    project = ProjectFactory(waiting=True, tasks=[TaskFactory(done=True)])

    with pytest.raises(InvalidProjectOperation):
        project.complete()


def test_complete_requires_finishable_project():
    project = ProjectFactory(in_progress=True, tasks=[TaskFactory(pending=True)])

    with pytest.raises(InvalidProjectOperation):
        project.complete()


# --- add_task() ---


def test_add_task_creates_pending_task():
    project = ProjectFactory(in_progress=True)

    task = project.add_task("Write docs", Priority.HIGH)

    assert task.status == TaskStatus.PENDING
    assert task.title == "Write docs"
    assert task.priority == Priority.HIGH
    assert task.project_id == project.id


def test_add_task_appends_to_project():
    project = ProjectFactory(in_progress=True)

    project.add_task("Task A", Priority.LOW)
    project.add_task("Task B", Priority.MEDIUM)

    assert len(project.tasks) == 2


def test_add_task_requires_active_project():
    project = ProjectFactory(waiting=True)

    with pytest.raises(InvalidProjectOperation):
        project.add_task("Task", Priority.LOW)


# --- complete_tasks() ---


def test_complete_tasks_marks_specified_done():
    t1 = TaskFactory(pending=True)
    t2 = TaskFactory(pending=True)
    project = ProjectFactory(in_progress=True, tasks=[t1, t2])

    project.complete_tasks({t1.id})

    assert t1.status == TaskStatus.DONE
    assert t2.status == TaskStatus.PENDING


def test_complete_tasks_sets_completed_at():
    task = TaskFactory(pending=True)
    project = ProjectFactory(in_progress=True, tasks=[task])

    project.complete_tasks({task.id})

    assert task.completed_at is not None


def test_complete_tasks_ignores_unknown_ids():
    task = TaskFactory(pending=True)
    project = ProjectFactory(in_progress=True, tasks=[task])

    project.complete_tasks({uuid4()})

    assert task.status == TaskStatus.PENDING


def test_complete_tasks_requires_active_project():
    task = TaskFactory(pending=True)
    project = ProjectFactory(waiting=True, tasks=[task])

    with pytest.raises(InvalidProjectOperation):
        project.complete_tasks({task.id})


# --- cancel_tasks() ---


def test_cancel_tasks_marks_specified_cancelled():
    t1 = TaskFactory(pending=True)
    t2 = TaskFactory(pending=True)
    project = ProjectFactory(in_progress=True, tasks=[t1, t2])

    project.cancel_tasks({t1.id})

    assert t1.status == TaskStatus.CANCELLED
    assert t2.status == TaskStatus.PENDING


def test_cancel_tasks_requires_active_project():
    task = TaskFactory(pending=True)
    project = ProjectFactory(waiting=True, tasks=[task])

    with pytest.raises(InvalidProjectOperation):
        project.cancel_tasks({task.id})


# --- complete_all_tasks() ---


def test_complete_all_tasks_marks_all_pending_done():
    t1 = TaskFactory(pending=True)
    t2 = TaskFactory(pending=True)
    project = ProjectFactory(in_progress=True, tasks=[t1, t2])

    project.complete_all_tasks()

    assert t1.status == TaskStatus.DONE
    assert t2.status == TaskStatus.DONE


def test_complete_all_tasks_skips_non_pending():
    t1 = TaskFactory(cancelled=True)
    t2 = TaskFactory(pending=True)
    project = ProjectFactory(in_progress=True, tasks=[t1, t2])

    project.complete_all_tasks()

    assert t1.status == TaskStatus.CANCELLED
    assert t2.status == TaskStatus.DONE


def test_complete_all_tasks_requires_active_project():
    project = ProjectFactory(waiting=True, tasks=[TaskFactory(pending=True)])

    with pytest.raises(InvalidProjectOperation):
        project.complete_all_tasks()


# --- remove_tasks() ---


def test_remove_tasks_removes_specified():
    t1 = TaskFactory()
    t2 = TaskFactory()
    project = ProjectFactory(in_progress=True, tasks=[t1, t2])

    project.remove_tasks({t1.id})

    assert len(project.tasks) == 1
    assert project.tasks[0].id == t2.id


def test_remove_tasks_ignores_unknown_ids():
    task = TaskFactory()
    project = ProjectFactory(in_progress=True, tasks=[task])

    project.remove_tasks({uuid4()})

    assert len(project.tasks) == 1


def test_remove_tasks_requires_active_project():
    task = TaskFactory()
    project = ProjectFactory(waiting=True, tasks=[task])

    with pytest.raises(InvalidProjectOperation):
        project.remove_tasks({task.id})


# --- deletion guard ---


def test_ensure_can_be_deleted_allows_waiting_project():
    project = ProjectFactory(waiting=True)

    project.ensure_can_be_deleted()


def test_ensure_can_be_deleted_rejects_in_progress_project():
    project = ProjectFactory(in_progress=True)

    with pytest.raises(InvalidProjectOperation):
        project.ensure_can_be_deleted()


# --- pending_count / can_finish / is_active ---


@pytest.mark.parametrize("n_pending,n_done", [(2, 1), (1, 0), (3, 3)])
def test_pending_count(n_pending, n_done):
    tasks = [TaskFactory(pending=True) for _ in range(n_pending)]
    tasks += [TaskFactory(done=True) for _ in range(n_done)]
    project = ProjectFactory(in_progress=True, tasks=tasks)

    assert project.pending_count == n_pending


def test_can_finish_when_all_tasks_done():
    tasks = [TaskFactory(done=True) for _ in range(3)]
    project = ProjectFactory(in_progress=True, tasks=tasks)

    assert project.can_finish is True
    assert project.pending_count == 0


def test_cannot_finish_with_pending_tasks():
    tasks = [TaskFactory(done=True), TaskFactory(pending=True)]
    project = ProjectFactory(in_progress=True, tasks=tasks)

    assert project.can_finish is False
