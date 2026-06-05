from uuid import UUID

from fastapi import HTTPException

from app.domain.project import Project
from app.repository.in_memory import repo as project_repository


def list_projects(sort: str = "name_asc") -> list[Project]:
    return project_repository.list_projects(sort)


def get_project(project_id: UUID) -> Project:
    project = project_repository.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def create_project(name: str) -> Project:
    return project_repository.create_project(name)


def delete_project(project_id: UUID) -> None:
    project = get_project(project_id)
    if not project.can_be_deleted:
        raise HTTPException(status_code=409, detail="Cannot delete an IN_PROGRESS project")
    project_repository.delete_project(project_id)


def start_project(project_id: UUID) -> Project:
    project = get_project(project_id)
    if not project.can_start:
        raise HTTPException(status_code=409, detail="Project must be WAITING to start")
    project.start()
    return project_repository.save_project(project)


def finish_project(project_id: UUID) -> Project:
    project = get_project(project_id)
    if not project.is_active:
        raise HTTPException(status_code=409, detail="Project must be IN_PROGRESS to finish")
    if not project.can_finish:
        raise HTTPException(status_code=409, detail="Project has pending tasks or no tasks")
    project.complete()
    return project_repository.save_project(project)


def cancel_project(project_id: UUID) -> Project:
    project = get_project(project_id)
    if not project.can_cancel:
        raise HTTPException(status_code=409, detail="Cannot cancel a DONE project")
    project.cancel()
    return project_repository.save_project(project)
