from datetime import UTC, datetime
from uuid import uuid4

from app.domain.task import Priority, Task, TaskStatus

NOW = datetime(2026, 6, 4, 12, 0, tzinfo=UTC)


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


# --- complete() ---


def test_complete_sets_status_to_done():
    task = _make_task()

    task.complete()

    assert task.status == TaskStatus.DONE


def test_complete_sets_completed_at():
    task = _make_task()

    task.complete()

    assert task.completed_at is not None
    assert task.completed_at.tzinfo is UTC


def test_complete_completed_at_is_after_created_at():
    task = _make_task()

    task.complete()

    assert task.completed_at > task.created_at


# --- cancel() ---


def test_cancel_sets_status_to_cancelled():
    task = _make_task()

    task.cancel()

    assert task.status == TaskStatus.CANCELLED


def test_cancel_does_not_set_completed_at():
    task = _make_task()

    task.cancel()

    assert task.completed_at is None
