from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.project import ProjectStatus
from app.ports.task_wire import TaskResponse


class ProjectCreate(BaseModel):
    name: str


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    status: ProjectStatus
    created_at: datetime
    completed_at: datetime | None = None
    tasks: list[TaskResponse] = []
    pending_count: int
    can_finish: bool
    is_active: bool


class ProjectListResponse(BaseModel):
    id: UUID
    name: str
    status: ProjectStatus
    created_at: datetime
    completed_at: datetime | None = None
    pending_count: int
    can_finish: bool
    is_active: bool
