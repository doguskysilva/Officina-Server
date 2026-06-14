from app.domain.project import Project
from app.repository.connection import get_repository


def seed_project(project: Project) -> Project:
    return get_repository().save_project(project)


def seed_projects(*projects: Project) -> list[Project]:
    return [get_repository().save_project(p) for p in projects]
