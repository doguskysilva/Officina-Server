from datetime import UTC, datetime
from uuid import uuid4

from app.domain.project import Project, ProjectStatus
from app.domain.task import Priority, Task, TaskStatus
from app.repository.connection import get_repository

# --- builders (no DB) ---


def waiting_project(name: str = "Project") -> Project:
    return Project(
        id=uuid4(),
        name=name,
        status=ProjectStatus.WAITING,
        created_at=datetime.now(UTC),
    )


def active_project(name: str = "Project") -> Project:
    return Project(
        id=uuid4(),
        name=name,
        status=ProjectStatus.IN_PROGRESS,
        created_at=datetime.now(UTC),
    )


def cancelled_project(name: str = "Project") -> Project:
    return Project(
        id=uuid4(),
        name=name,
        status=ProjectStatus.CANCELLED,
        created_at=datetime.now(UTC),
    )


def done_project(name: str = "Project") -> Project:
    project_id = uuid4()
    now = datetime.now(UTC)
    task = Task(
        id=uuid4(),
        project_id=project_id,
        title="Done task",
        status=TaskStatus.DONE,
        priority=Priority.MEDIUM,
        created_at=now,
        completed_at=now,
    )
    return Project(
        id=project_id,
        name=name,
        status=ProjectStatus.DONE,
        created_at=now,
        completed_at=now,
        tasks=[task],
    )


def active_project_with_task(
    task_title: str = "Task",
    priority: Priority = Priority.MEDIUM,
    project_name: str = "Project",
) -> tuple[Project, Task]:
    project_id = uuid4()
    task = Task(
        id=uuid4(),
        project_id=project_id,
        title=task_title,
        status=TaskStatus.PENDING,
        priority=priority,
        created_at=datetime.now(UTC),
    )
    project = Project(
        id=project_id,
        name=project_name,
        status=ProjectStatus.IN_PROGRESS,
        created_at=datetime.now(UTC),
        tasks=[task],
    )
    return project, task


def active_project_with_tasks(
    count: int = 3,
    project_name: str = "Project",
) -> Project:
    project_id = uuid4()
    now = datetime.now(UTC)
    tasks = [
        Task(
            id=uuid4(),
            project_id=project_id,
            title=f"Task {i + 1}",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            created_at=now,
        )
        for i in range(count)
    ]
    return Project(
        id=project_id,
        name=project_name,
        status=ProjectStatus.IN_PROGRESS,
        created_at=now,
        tasks=tasks,
    )


def active_project_with_done_task(
    project_name: str = "Project",
) -> tuple[Project, Task]:
    """Active project whose only task is DONE — can_finish is True."""
    project_id = uuid4()
    now = datetime.now(UTC)
    task = Task(
        id=uuid4(),
        project_id=project_id,
        title="Done task",
        status=TaskStatus.DONE,
        priority=Priority.MEDIUM,
        created_at=now,
        completed_at=now,
    )
    project = Project(
        id=project_id,
        name=project_name,
        status=ProjectStatus.IN_PROGRESS,
        created_at=now,
        tasks=[task],
    )
    return project, task


# --- seed ---


def seed_project(project: Project) -> Project:
    return get_repository().save_project(project)


def seed_projects(*projects: Project) -> list[Project]:
    return [get_repository().save_project(p) for p in projects]
