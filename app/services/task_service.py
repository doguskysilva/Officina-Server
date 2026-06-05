from uuid import UUID

from fastapi import HTTPException

from app.domain.project import Project
from app.domain.task import Priority, Task
from app.repository.in_memory import repo as project_repository
from app.services import project_service


def add_task(project_id: UUID, title: str, priority: Priority) -> Task:
    project = project_service.get_project(project_id)
    if not project.is_active:
        raise HTTPException(status_code=409, detail="Project must be IN_PROGRESS to add tasks")
    task = project.add_task(title, priority)
    project_repository.save_project(project)
    return task


def complete_tasks(project_id: UUID, task_ids: set[UUID]) -> Project:
    project = project_service.get_project(project_id)
    if not project.is_active:
        raise HTTPException(status_code=409, detail="Project must be IN_PROGRESS to complete tasks")
    project.complete_tasks(task_ids)
    return project_repository.save_project(project)


def cancel_tasks(project_id: UUID, task_ids: set[UUID]) -> Project:
    project = project_service.get_project(project_id)
    if not project.is_active:
        raise HTTPException(status_code=409, detail="Project must be IN_PROGRESS to cancel tasks")
    project.cancel_tasks(task_ids)
    return project_repository.save_project(project)


def complete_all_tasks(project_id: UUID) -> Project:
    project = project_service.get_project(project_id)
    if not project.is_active:
        raise HTTPException(status_code=409, detail="Project must be IN_PROGRESS to complete tasks")
    project.complete_all_tasks()
    return project_repository.save_project(project)


def remove_tasks(project_id: UUID, task_ids: set[UUID]) -> Project:
    project = project_service.get_project(project_id)
    if not project.is_active:
        raise HTTPException(status_code=409, detail="Project must be IN_PROGRESS to remove tasks")
    project.remove_tasks(task_ids)
    return project_repository.save_project(project)


