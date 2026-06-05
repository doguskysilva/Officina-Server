from datetime import UTC, datetime

from app.adapters import task_model_adapter
from app.domain.project import Project, ProjectStatus
from app.repository.models import ProjectModel


def _naive(dt: datetime | None) -> datetime | None:
    return dt.replace(tzinfo=None) if dt is not None else None


def _aware(dt: datetime | None) -> datetime | None:
    return dt.replace(tzinfo=UTC) if dt is not None else None


def to_model(project: Project) -> ProjectModel:
    return ProjectModel(
        id=project.id,
        name=project.name,
        status=project.status.value,
        created_at=_naive(project.created_at),
        completed_at=_naive(project.completed_at),
    )


def from_model(model: ProjectModel) -> Project:
    return Project(
        id=model.id,
        name=model.name,
        status=ProjectStatus(model.status),
        created_at=_aware(model.created_at),
        completed_at=_aware(model.completed_at),
        tasks=[task_model_adapter.from_model(t) for t in model.tasks],
    )
