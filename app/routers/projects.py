from uuid import UUID

from fastapi import APIRouter

from app.adapters import project_adapter, task_adapter
from app.ports.project_wire import ProjectCreate, ProjectResponse
from app.ports.task_wire import TaskCreate, TaskIdsRequest, TaskResponse
from app.services import project_service, task_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
def list_projects(sort: str = "name_asc") -> list[ProjectResponse]:
    return [project_adapter.record_to_response(p) for p in project_service.list_projects(sort)]


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(body: ProjectCreate) -> ProjectResponse:
    name = project_adapter.from_create_request(body)
    return project_adapter.record_to_response(project_service.create_project(name))


@router.get("/{id}", response_model=ProjectResponse)
def get_project(id: UUID) -> ProjectResponse:
    return project_adapter.record_to_response(project_service.get_project(id))


@router.delete("/{id}", status_code=204)
def delete_project(id: UUID) -> None:
    project_service.delete_project(id)


@router.post("/{id}/start", response_model=ProjectResponse)
def start_project(id: UUID) -> ProjectResponse:
    return project_adapter.record_to_response(project_service.start_project(id))


@router.post("/{id}/finish", response_model=ProjectResponse)
def finish_project(id: UUID) -> ProjectResponse:
    return project_adapter.record_to_response(project_service.finish_project(id))


@router.post("/{id}/cancel", response_model=ProjectResponse)
def cancel_project(id: UUID) -> ProjectResponse:
    return project_adapter.record_to_response(project_service.cancel_project(id))


@router.post("/{id}/tasks", response_model=TaskResponse, status_code=201)
def add_task(id: UUID, body: TaskCreate) -> TaskResponse:
    return task_adapter.record_to_response(task_service.add_task(id, body.title, body.priority))


@router.patch("/{id}/tasks/complete", response_model=ProjectResponse)
def complete_tasks(id: UUID, body: TaskIdsRequest) -> ProjectResponse:
    return project_adapter.record_to_response(task_service.complete_tasks(id, set(body.task_ids)))


@router.patch("/{id}/tasks/cancel", response_model=ProjectResponse)
def cancel_tasks(id: UUID, body: TaskIdsRequest) -> ProjectResponse:
    return project_adapter.record_to_response(task_service.cancel_tasks(id, set(body.task_ids)))


@router.patch("/{id}/tasks/complete-all", response_model=ProjectResponse)
def complete_all_tasks(id: UUID) -> ProjectResponse:
    return project_adapter.record_to_response(task_service.complete_all_tasks(id))


@router.delete("/{id}/tasks", response_model=ProjectResponse)
def remove_tasks(id: UUID, body: TaskIdsRequest) -> ProjectResponse:
    return project_adapter.record_to_response(task_service.remove_tasks(id, set(body.task_ids)))
