from uuid import UUID

from sqlalchemy import Engine, case, func
from sqlmodel import Session, delete, select, text

from app.adapters import project_adapter, task_adapter
from app.adapters.datetime_adapter import to_aware
from app.domain.project import Project, ProjectStatus, ProjectSummary
from app.repository.base import ProjectSort
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

    def list_projects(
        self,
        sort: ProjectSort = ProjectSort.NAME_ASC,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> list[ProjectSummary]:
        pending_count = func.coalesce(
            func.sum(case((TaskModel.status == "PENDING", 1), else_=0)),
            0,
        ).label("pending_count")
        task_count = func.count(TaskModel.id).label("task_count")
        stmt = (
            select(
                ProjectModel.id,
                ProjectModel.name,
                ProjectModel.status,
                ProjectModel.created_at,
                ProjectModel.completed_at,
                task_count,
                pending_count,
            )
            .outerjoin(TaskModel, TaskModel.project_id == ProjectModel.id)
            .group_by(
                ProjectModel.id,
                ProjectModel.name,
                ProjectModel.status,
                ProjectModel.created_at,
                ProjectModel.completed_at,
            )
            .order_by(*self._order_by_for(sort))
            .offset(offset)
            .limit(limit)
        )
        with Session(self._engine) as session:
            rows = session.exec(stmt).all()
        summaries: list[ProjectSummary] = []
        for row in rows:
            (
                project_id,
                name,
                status_raw,
                created_at,
                completed_at,
                task_count_value,
                pending_count_value,
            ) = row
            status = ProjectStatus(status_raw)
            total_tasks = int(task_count_value or 0)
            pending_tasks = int(pending_count_value or 0)
            summaries.append(
                ProjectSummary(
                    id=project_id,
                    name=name,
                    status=status,
                    created_at=to_aware(created_at),
                    completed_at=to_aware(completed_at),
                    pending_count=pending_tasks,
                    can_finish=total_tasks > 0 and pending_tasks == 0,
                    is_active=status == ProjectStatus.IN_PROGRESS,
                )
            )
        return summaries

    def get_project(self, project_id: UUID) -> Project | None:
        with Session(self._engine) as session:
            row = session.get(ProjectModel, project_id)
            if row is None:
                return None
            return project_adapter.from_model(row)

    def save_project(self, project: Project) -> Project:
        with Session(self._engine) as session:
            session.merge(project_adapter.to_model(project))
            existing_task_models = session.exec(
                select(TaskModel).where(TaskModel.project_id == project.id)
            ).all()
            existing_tasks_by_id = {
                task_model.id: task_model for task_model in existing_task_models
            }
            incoming_task_ids: set[UUID] = set()
            for task in project.tasks:
                incoming_task_ids.add(task.id)
                task_model = existing_tasks_by_id.get(task.id)
                if task_model is None:
                    session.add(task_adapter.to_model(task))
                    continue
                updated_model = task_adapter.to_model(task)
                task_model.title = updated_model.title
                task_model.status = updated_model.status
                task_model.priority = updated_model.priority
                task_model.created_at = updated_model.created_at
                task_model.completed_at = updated_model.completed_at
            removed_task_ids = set(existing_tasks_by_id) - incoming_task_ids
            if removed_task_ids:
                session.exec(delete(TaskModel).where(TaskModel.id.in_(removed_task_ids)))
            session.commit()
        return project

    def delete_project(self, project_id: UUID) -> None:
        with Session(self._engine) as session:
            session.exec(delete(TaskModel).where(TaskModel.project_id == project_id))
            row = session.get(ProjectModel, project_id)
            if row:
                session.delete(row)
            session.commit()

    @staticmethod
    def _order_by_for(sort: ProjectSort) -> tuple:
        if sort == ProjectSort.NEWEST:
            return (ProjectModel.created_at.desc(), ProjectModel.id.asc())
        if sort == ProjectSort.OLDEST:
            return (ProjectModel.created_at.asc(), ProjectModel.id.asc())
        return (ProjectModel.name.asc(), ProjectModel.id.asc())
