from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class TaskModel(SQLModel, table=True):
    __tablename__ = "task"

    id: str = Field(primary_key=True)
    project_id: str = Field(foreign_key="project.id", index=True)
    title: str
    status: str
    priority: str
    created_at: datetime
    completed_at: datetime | None = Field(default=None)


class ProjectModel(SQLModel, table=True):
    __tablename__ = "project"

    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    status: str
    created_at: datetime
    completed_at: datetime | None = Field(default=None)

    tasks: list[TaskModel] = Relationship()
