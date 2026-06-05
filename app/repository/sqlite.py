from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Engine
from sqlmodel import Session, delete, select, text

from app.adapters import project_model_adapter, task_model_adapter
from app.domain.project import Project, ProjectStatus
from app.repository.models import ProjectModel, TaskModel


class SQLiteProjectRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def ping(self) -> bool:
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def list_projects(self, sort: str = "name_asc") -> list[Project]:
        with Session(self._engine) as session:
            rows = session.exec(select(ProjectModel)).all()
            projects = [project_model_adapter.from_model(r) for r in rows]
        if sort == "newest":
            return sorted(projects, key=lambda p: p.created_at, reverse=True)
        if sort == "oldest":
            return sorted(projects, key=lambda p: p.created_at)
        return sorted(projects, key=lambda p: p.name)

    def get_project(self, project_id: UUID) -> Project | None:
        with Session(self._engine) as session:
            row = session.get(ProjectModel, project_id)
            if row is None:
                return None
            return project_model_adapter.from_model(row)

    def create_project(self, name: str) -> Project:
        project = Project(
            id=uuid4(),
            name=name,
            status=ProjectStatus.WAITING,
            created_at=datetime.now(UTC),
        )
        with Session(self._engine) as session:
            session.add(project_model_adapter.to_model(project))
            session.commit()
        return project

    def save_project(self, project: Project) -> Project:
        with Session(self._engine) as session:
            session.merge(project_model_adapter.to_model(project))
            session.exec(delete(TaskModel).where(TaskModel.project_id == project.id))
            for task in project.tasks:
                session.add(task_model_adapter.to_model(task))
            session.commit()
        return project

    def delete_project(self, project_id: UUID) -> None:
        with Session(self._engine) as session:
            session.exec(delete(TaskModel).where(TaskModel.project_id == project_id))
            row = session.get(ProjectModel, project_id)
            if row:
                session.delete(row)
            session.commit()
