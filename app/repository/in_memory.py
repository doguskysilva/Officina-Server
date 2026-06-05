from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.project import Project, ProjectStatus


class InMemoryRepository:
    def __init__(self) -> None:
        self._projects: dict[UUID, Project] = {}

    def list_projects(self, sort: str = "name_asc") -> list[Project]:
        projects = list(self._projects.values())
        if sort == "newest":
            return sorted(projects, key=lambda p: p.created_at, reverse=True)
        if sort == "oldest":
            return sorted(projects, key=lambda p: p.created_at)
        return sorted(projects, key=lambda p: p.name)

    def get_project(self, project_id: UUID) -> Project | None:
        return self._projects.get(project_id)

    def create_project(self, name: str) -> Project:
        project = Project(
            id=uuid4(),
            name=name,
            status=ProjectStatus.WAITING,
            created_at=datetime.now(UTC),
        )
        self._projects[project.id] = project
        return project

    def save_project(self, project: Project) -> Project:
        self._projects[project.id] = project
        return project

    def delete_project(self, project_id: UUID) -> None:
        self._projects.pop(project_id, None)


repo = InMemoryRepository()
