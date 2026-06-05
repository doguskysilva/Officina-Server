from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.adapters.project_model_adapter import from_model, to_model
from app.domain.project import Project, ProjectStatus
from app.domain.task import Priority, Task, TaskStatus
from app.repository.models import ProjectModel, TaskModel

PROJECT_ID = uuid4()
TASK_ID = uuid4()
NOW = datetime(2026, 6, 4, 12, 0, tzinfo=UTC)
COMPLETED = datetime(2026, 6, 5, 10, 0, tzinfo=UTC)


def _make_project(**kwargs) -> Project:
    defaults = dict(
        id=PROJECT_ID,
        name="App Mobile",
        status=ProjectStatus.WAITING,
        created_at=NOW,
    )
    return Project(**{**defaults, **kwargs})


def _make_model(tasks: list[TaskModel] | None = None, **kwargs) -> ProjectModel:
    defaults = dict(
        id=str(PROJECT_ID),
        name="App Mobile",
        status="WAITING",
        created_at=NOW.replace(tzinfo=None),
    )
    model = ProjectModel(**{**defaults, **kwargs})
    model.tasks = tasks or []
    return model


def _make_task_model(**kwargs) -> TaskModel:
    defaults = dict(
        id=str(TASK_ID),
        project_id=str(PROJECT_ID),
        title="Task",
        status="PENDING",
        priority="MEDIUM",
        created_at=NOW.replace(tzinfo=None),
    )
    return TaskModel(**{**defaults, **kwargs})


# --- to_model ---


def test_to_model_converts_id_to_str():
    model = to_model(_make_project())

    assert model.id == str(PROJECT_ID)
    assert isinstance(model.id, str)


def test_to_model_maps_name_and_status():
    model = to_model(_make_project())

    assert model.name == "App Mobile"
    assert model.status == "WAITING"


def test_to_model_strips_timezone():
    model = to_model(_make_project())

    assert model.created_at.tzinfo is None


def test_to_model_completed_at_none():
    model = to_model(_make_project())

    assert model.completed_at is None


def test_to_model_strips_timezone_from_completed_at():
    model = to_model(_make_project(status=ProjectStatus.DONE, completed_at=COMPLETED))

    assert model.completed_at is not None
    assert model.completed_at.tzinfo is None


def test_to_model_does_not_include_tasks():
    project = _make_project()
    project.tasks = [
        Task(
            id=TASK_ID,
            project_id=PROJECT_ID,
            title="Task",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            created_at=NOW,
        )
    ]

    model = to_model(project)

    assert model.tasks == []


# --- from_model ---


def test_from_model_converts_id_to_uuid():
    project = from_model(_make_model())

    assert project.id == PROJECT_ID
    assert isinstance(project.id, UUID)


def test_from_model_maps_name_and_status():
    project = from_model(_make_model())

    assert project.name == "App Mobile"
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
    task_model = _make_task_model()
    project = from_model(_make_model(tasks=[task_model]))

    assert len(project.tasks) == 1
    assert project.tasks[0].id == TASK_ID
    assert project.tasks[0].status == TaskStatus.PENDING


def test_from_model_reconstructs_all_project_statuses():
    for status in ("WAITING", "IN_PROGRESS", "DONE", "CANCELLED"):
        project = from_model(_make_model(status=status))
        assert project.status == ProjectStatus(status)
