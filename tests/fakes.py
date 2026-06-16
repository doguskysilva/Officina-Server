from uuid import UUID

from app.domain.project import Project, ProjectSummary
from app.repository.base import ProjectSort


class FakeRepository:
    def __init__(self, projects: list[Project] | None = None) -> None:
        self._store: dict[UUID, Project] = {p.id: p for p in (projects or [])}

    def ping(self) -> bool:
        return True

    def list_projects(
        self,
        sort: ProjectSort = ProjectSort.NAME_ASC,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> list[ProjectSummary]:
        projects = list(self._store.values())
        if sort == ProjectSort.NEWEST:
            ordered = sorted(projects, key=lambda p: p.created_at, reverse=True)
        elif sort == ProjectSort.OLDEST:
            ordered = sorted(projects, key=lambda p: p.created_at)
        else:
            ordered = sorted(projects, key=lambda p: p.name)
        page = ordered[offset : offset + limit]
        return [
            ProjectSummary(
                id=project.id,
                name=project.name,
                status=project.status,
                created_at=project.created_at,
                completed_at=project.completed_at,
                pending_count=project.pending_count,
                can_finish=project.can_finish,
                is_active=project.is_active,
            )
            for project in page
        ]

    def get_project(self, project_id: UUID) -> Project | None:
        return self._store.get(project_id)

    def save_project(self, project: Project) -> Project:
        self._store[project.id] = project
        return project

    def delete_project(self, project_id: UUID) -> None:
        self._store.pop(project_id, None)
