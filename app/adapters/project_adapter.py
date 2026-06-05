from app.adapters import task_adapter
from app.domain.project import Project
from app.ports.project_wire import ProjectCreate, ProjectResponse


def from_create_request(body: ProjectCreate) -> str:
    return body.name


def record_to_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        status=project.status,
        created_at=project.created_at,
        completed_at=project.completed_at,
        tasks=[task_adapter.record_to_response(t) for t in project.tasks],
        pending_count=project.pending_count,
        can_finish=project.can_finish,
        is_active=project.is_active,
    )
