from enum import StrEnum
from typing import Protocol, runtime_checkable
from uuid import UUID

from app.domain.project import Project, ProjectSummary


class ProjectSort(StrEnum):
    NAME_ASC = "name_asc"
    NEWEST = "newest"
    OLDEST = "oldest"


@runtime_checkable
class ProjectRepository(Protocol):
    def ping(self) -> bool: ...
    def list_projects(
        self,
        sort: ProjectSort = ProjectSort.NAME_ASC,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> list[ProjectSummary]: ...
    def get_project(self, project_id: UUID) -> Project | None: ...
    def save_project(self, project: Project) -> Project: ...
    def delete_project(self, project_id: UUID) -> None: ...
