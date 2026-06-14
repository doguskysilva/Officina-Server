from uuid import UUID

from app.domain.project import Project
from app.repository.base import ProjectRepository
from app.services.exceptions import ProjectConflict, ProjectNotFound


class ProjectService:
    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    def list_projects(self, sort: str = "name_asc") -> list[Project]:
        return self._repository.list_projects(sort)

    def get_project(self, project_id: UUID) -> Project:
        project = self._repository.get_project(project_id)
        if project is None:
            raise ProjectNotFound()
        return project

    def create_project(self, name: str) -> Project:
        return self._repository.create_project(name)

    def delete_project(self, project_id: UUID) -> None:
        project = self.get_project(project_id)
        if not project.can_be_deleted:
            raise ProjectConflict("Cannot delete an IN_PROGRESS project")
        self._repository.delete_project(project_id)

    def start_project(self, project_id: UUID) -> Project:
        project = self.get_project(project_id)
        if not project.can_start:
            raise ProjectConflict("Project must be WAITING to start")
        project.start()
        return self._repository.save_project(project)

    def finish_project(self, project_id: UUID) -> Project:
        project = self.get_project(project_id)
        if not project.is_active:
            raise ProjectConflict("Project must be IN_PROGRESS to finish")
        if not project.can_finish:
            raise ProjectConflict("Project has pending tasks or no tasks")
        project.complete()
        return self._repository.save_project(project)

    def cancel_project(self, project_id: UUID) -> Project:
        project = self.get_project(project_id)
        if not project.can_cancel:
            raise ProjectConflict("Cannot cancel a DONE project")
        project.cancel()
        return self._repository.save_project(project)
