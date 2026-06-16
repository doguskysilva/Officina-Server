from uuid import UUID

from app.domain.exceptions import InvalidProjectOperation
from app.domain.project import Project, ProjectSummary
from app.repository.base import ProjectRepository, ProjectSort
from app.services.exceptions import ProjectConflict, ProjectNotFound


class ProjectService:
    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    def list_projects(
        self,
        sort: ProjectSort = ProjectSort.NAME_ASC,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> list[ProjectSummary]:
        return self._repository.list_projects(sort, offset=offset, limit=limit)

    def get_project(self, project_id: UUID) -> Project:
        project = self._repository.get_project(project_id)
        if project is None:
            raise ProjectNotFound()
        return project

    def create_project(self, name: str) -> Project:
        return self._repository.save_project(Project.create(name))

    def delete_project(self, project_id: UUID) -> None:
        project = self.get_project(project_id)
        self._run_project_operation(project.ensure_can_be_deleted)
        self._repository.delete_project(project_id)

    def start_project(self, project_id: UUID) -> Project:
        project = self.get_project(project_id)
        self._run_project_operation(project.start)
        return self._repository.save_project(project)

    def finish_project(self, project_id: UUID) -> Project:
        project = self.get_project(project_id)
        self._run_project_operation(project.complete)
        return self._repository.save_project(project)

    def cancel_project(self, project_id: UUID) -> Project:
        project = self.get_project(project_id)
        self._run_project_operation(project.cancel)
        return self._repository.save_project(project)

    def _run_project_operation(self, operation) -> None:
        try:
            operation()
        except InvalidProjectOperation as exc:
            raise ProjectConflict(str(exc)) from exc
