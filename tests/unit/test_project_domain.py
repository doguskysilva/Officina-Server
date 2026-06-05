from datetime import UTC, datetime
from uuid import uuid4

from app.domain.project import Project, ProjectStatus
from app.domain.task import Priority, Task, TaskStatus

NOW = datetime(2026, 6, 4, 12, 0, tzinfo=UTC)


def _make_project(**kwargs) -> Project:
    defaults = dict(id=uuid4(), name="My Project", status=ProjectStatus.IN_PROGRESS, created_at=NOW)
    return Project(**{**defaults, **kwargs})


def _make_task(**kwargs) -> Task:
    defaults = dict(
        id=uuid4(),
        project_id=uuid4(),
        title="Task",
        status=TaskStatus.DONE,
        priority=Priority.MEDIUM,
        created_at=NOW,
    )
    return Task(**{**defaults, **kwargs})


# --- start() ---


def test_start_sets_status_to_in_progress():
    project = _make_project(status=ProjectStatus.WAITING)

    project.start()

    assert project.status == ProjectStatus.IN_PROGRESS


def test_start_makes_project_active():
    project = _make_project(status=ProjectStatus.WAITING)

    project.start()

    assert project.is_active is True


def test_start_disables_can_start():
    project = _make_project(status=ProjectStatus.WAITING)

    project.start()

    assert project.can_start is False


# --- cancel() ---


def test_cancel_sets_status_to_cancelled():
    project = _make_project(status=ProjectStatus.WAITING)

    project.cancel()

    assert project.status == ProjectStatus.CANCELLED


def test_cancel_from_in_progress():
    project = _make_project(status=ProjectStatus.IN_PROGRESS)

    project.cancel()

    assert project.status == ProjectStatus.CANCELLED
    assert project.is_active is False


# --- complete() ---


def test_complete_sets_status_to_done():
    project = _make_project()

    project.complete()

    assert project.status == ProjectStatus.DONE


def test_complete_sets_completed_at():
    project = _make_project()

    project.complete()

    assert project.completed_at is not None
    assert project.completed_at.tzinfo is UTC


def test_complete_completed_at_is_after_created_at():
    project = _make_project()

    project.complete()

    assert project.completed_at > project.created_at


def test_complete_updates_can_finish_derived_state():
    tasks = [_make_task(status=TaskStatus.DONE)]
    project = _make_project(tasks=tasks)

    project.complete()

    assert project.status == ProjectStatus.DONE
    assert not project.is_active
    assert not project.can_cancel
