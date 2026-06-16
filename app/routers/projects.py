from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.adapters import project_adapter, task_adapter
from app.ports.project_wire import ProjectCreate, ProjectListResponse, ProjectResponse
from app.ports.task_wire import TaskCreate, TaskIdsRequest, TaskResponse
from app.repository.base import ProjectRepository, ProjectSort
from app.repository.connection import get_repository
from app.services.project_service import ProjectService
from app.services.task_service import TaskService

router = APIRouter(prefix="/projects", tags=["projects"])

ProjectRepositoryDep = Annotated[ProjectRepository, Depends(get_repository)]


def get_project_service(repository: ProjectRepositoryDep) -> ProjectService:
    return ProjectService(repository)


def get_task_service(repository: ProjectRepositoryDep) -> TaskService:
    return TaskService(repository)


@router.get("", response_model=list[ProjectListResponse])
def list_projects(
    project_service: Annotated[ProjectService, Depends(get_project_service)],
    sort: ProjectSort = ProjectSort.NAME_ASC,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[ProjectListResponse]:
    return [
        project_adapter.to_list_response(p)
        for p in project_service.list_projects(sort, offset=offset, limit=limit)
    ]


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(
    body: ProjectCreate,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    name = project_adapter.from_request(body)
    return project_adapter.to_response(project_service.create_project(name))


@router.get("/{id}", response_model=ProjectResponse)
def get_project(
    id: UUID,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    return project_adapter.to_response(project_service.get_project(id))


@router.delete("/{id}", status_code=204)
def delete_project(
    id: UUID,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
) -> None:
    project_service.delete_project(id)


@router.post("/{id}/start", response_model=ProjectResponse)
def start_project(
    id: UUID,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    return project_adapter.to_response(project_service.start_project(id))


@router.post("/{id}/finish", response_model=ProjectResponse)
def finish_project(
    id: UUID,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    return project_adapter.to_response(project_service.finish_project(id))


@router.post("/{id}/cancel", response_model=ProjectResponse)
def cancel_project(
    id: UUID,
    project_service: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    return project_adapter.to_response(project_service.cancel_project(id))


@router.post("/{id}/tasks", response_model=TaskResponse, status_code=201)
def add_task(
    id: UUID,
    body: TaskCreate,
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    return task_adapter.to_response(task_service.add_task(id, body.title, body.priority))


@router.patch("/{id}/tasks/complete", response_model=ProjectResponse)
def complete_tasks(
    id: UUID,
    body: TaskIdsRequest,
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> ProjectResponse:
    return project_adapter.to_response(task_service.complete_tasks(id, set(body.task_ids)))


@router.patch("/{id}/tasks/cancel", response_model=ProjectResponse)
def cancel_tasks(
    id: UUID,
    body: TaskIdsRequest,
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> ProjectResponse:
    return project_adapter.to_response(task_service.cancel_tasks(id, set(body.task_ids)))


@router.patch("/{id}/tasks/complete-all", response_model=ProjectResponse)
def complete_all_tasks(
    id: UUID,
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> ProjectResponse:
    return project_adapter.to_response(task_service.complete_all_tasks(id))


@router.delete("/{id}/tasks", response_model=ProjectResponse)
def remove_tasks(
    id: UUID,
    body: TaskIdsRequest,
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> ProjectResponse:
    return project_adapter.to_response(task_service.remove_tasks(id, set(body.task_ids)))
