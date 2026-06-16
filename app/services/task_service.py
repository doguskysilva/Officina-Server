from uuid import UUID

from app.domain.exceptions import DomainError
from app.domain.project import Project
from app.domain.task import Priority, Task
from app.repository.base import ProjectRepository
from app.services.exceptions import ProjectConflict, ProjectNotFound


class TaskService:
    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    def add_task(self, project_id: UUID, title: str, priority: Priority) -> Task:
        project = self._get_project(project_id)
        task = self._run_project_operation(lambda: project.add_task(title, priority))
        self._repository.save_project(project)
        return task

    def complete_tasks(self, project_id: UUID, task_ids: set[UUID]) -> Project:
        project = self._get_project(project_id)
        self._run_project_operation(lambda: project.complete_tasks(task_ids))
        return self._repository.save_project(project)

    def cancel_tasks(self, project_id: UUID, task_ids: set[UUID]) -> Project:
        project = self._get_project(project_id)
        self._run_project_operation(lambda: project.cancel_tasks(task_ids))
        return self._repository.save_project(project)

    def complete_all_tasks(self, project_id: UUID) -> Project:
        project = self._get_project(project_id)
        self._run_project_operation(project.complete_all_tasks)
        return self._repository.save_project(project)

    def remove_tasks(self, project_id: UUID, task_ids: set[UUID]) -> Project:
        project = self._get_project(project_id)
        self._run_project_operation(lambda: project.remove_tasks(task_ids))
        return self._repository.save_project(project)

    def _get_project(self, project_id: UUID) -> Project:
        project = self._repository.get_project(project_id)
        if project is None:
            raise ProjectNotFound()
        return project

    def _run_project_operation(self, operation):
        try:
            return operation()
        except DomainError as exc:
            raise ProjectConflict(str(exc)) from exc
