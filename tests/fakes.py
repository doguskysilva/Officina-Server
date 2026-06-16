from uuid import UUID

from app.domain.project import Project
from app.repository.base import ProjectSort


class FakeRepository:
    def __init__(self, projects: list[Project] | None = None) -> None:
        self._store: dict[UUID, Project] = {p.id: p for p in (projects or [])}

    def ping(self) -> bool:
        return True

    def list_projects(self, sort: ProjectSort = ProjectSort.NAME_ASC) -> list[Project]:
        projects = list(self._store.values())
        if sort == ProjectSort.NEWEST:
            return sorted(projects, key=lambda p: p.created_at, reverse=True)
        if sort == ProjectSort.OLDEST:
            return sorted(projects, key=lambda p: p.created_at)
        return sorted(projects, key=lambda p: p.name)

    def get_project(self, project_id: UUID) -> Project | None:
        return self._store.get(project_id)

    def save_project(self, project: Project) -> Project:
        self._store[project.id] = project
        return project

    def delete_project(self, project_id: UUID) -> None:
        self._store.pop(project_id, None)
