from datetime import UTC

from tests.factories import TaskFactory

# --- complete() ---


def test_complete_sets_status_to_done():
    task = TaskFactory()

    task.complete()

    assert task.status.value == "DONE"


def test_complete_sets_completed_at():
    task = TaskFactory()

    task.complete()

    assert task.completed_at is not None
    assert task.completed_at.tzinfo is UTC


def test_complete_completed_at_is_after_created_at():
    task = TaskFactory()

    task.complete()

    assert task.completed_at > task.created_at


# --- cancel() ---


def test_cancel_sets_status_to_cancelled():
    task = TaskFactory()

    task.cancel()

    assert task.status.value == "CANCELLED"


def test_cancel_does_not_set_completed_at():
    task = TaskFactory()

    task.cancel()

    assert task.completed_at is None
