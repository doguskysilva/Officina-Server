from app.adapters import task_adapter
from app.adapters.datetime_adapter import to_aware, to_naive
from app.domain.project import Project, ProjectStatus, ProjectSummary
from app.ports.project_wire import ProjectCreate, ProjectListResponse, ProjectResponse
from app.repository.models import ProjectModel


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


def to_list_response(project: ProjectSummary) -> ProjectListResponse:
    return ProjectListResponse(
        id=project.id,
        name=project.name,
        status=project.status,
        created_at=project.created_at,
        completed_at=project.completed_at,
        pending_count=project.pending_count,
        can_finish=project.can_finish,
        is_active=project.is_active,
    )


def to_model(project: Project) -> ProjectModel:
    return ProjectModel(
        id=project.id,
        name=project.name,
        status=project.status.value,
        created_at=to_naive(project.created_at),
        completed_at=to_naive(project.completed_at),
    )


def from_model(model: ProjectModel) -> Project:
    return Project(
        id=model.id,
        name=model.name,
        status=ProjectStatus(model.status),
        created_at=to_aware(model.created_at),
        completed_at=to_aware(model.completed_at),
        tasks=[task_adapter.from_model(t) for t in model.tasks],
    )
