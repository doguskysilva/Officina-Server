from datetime import UTC

import pytest

from app.domain.exceptions import InvalidTaskOperation
from app.domain.task import TaskStatus
from tests.factories import TaskFactory

# --- complete() ---


def test_complete_sets_status_to_done():
    task = TaskFactory(pending=True)

    task.complete()

    assert task.status.value == "DONE"


def test_complete_sets_completed_at():
    task = TaskFactory(pending=True)

    task.complete()

    assert task.completed_at is not None
    assert task.completed_at.tzinfo is UTC


def test_complete_completed_at_is_after_created_at():
    task = TaskFactory(pending=True)

    task.complete()

    assert task.completed_at > task.created_at


@pytest.mark.parametrize("status", [TaskStatus.DONE, TaskStatus.CANCELLED])
def test_complete_requires_pending_task(status):
    task = TaskFactory(status=status)

    with pytest.raises(InvalidTaskOperation):
        task.complete()


# --- cancel() ---


def test_cancel_sets_status_to_cancelled():
    task = TaskFactory(pending=True)

    task.cancel()

    assert task.status.value == "CANCELLED"


def test_cancel_does_not_set_completed_at():
    task = TaskFactory(pending=True)

    task.cancel()

    assert task.completed_at is None


@pytest.mark.parametrize("status", [TaskStatus.DONE, TaskStatus.CANCELLED])
def test_cancel_requires_pending_task(status):
    task = TaskFactory(status=status)

    with pytest.raises(InvalidTaskOperation):
        task.cancel()
