from datetime import UTC, datetime

from app.adapters import task_adapter
from app.domain.project import Project, ProjectStatus
from app.ports.project_wire import ProjectCreate, ProjectResponse
from app.repository.models import ProjectModel


def _naive(dt: datetime | None) -> datetime | None:
    return dt.replace(tzinfo=None) if dt is not None else None


def _aware(dt: datetime | None) -> datetime | None:
    return dt.replace(tzinfo=UTC) if dt is not None else None


def from_request(body: ProjectCreate) -> str:
    return body.name


def to_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        status=project.status,
        created_at=project.created_at,
        completed_at=project.completed_at,
        tasks=[task_adapter.to_response(t) for t in project.tasks],
        pending_count=project.pending_count,
        can_finish=project.can_finish,
        is_active=project.is_active,
    )


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
        tasks=[task_adapter.from_model(t) for t in model.tasks],
    )
