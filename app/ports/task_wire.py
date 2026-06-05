from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.task import Priority, TaskStatus


class TaskCreate(BaseModel):
    title: str
    priority: Priority


class TaskIdsRequest(BaseModel):
    task_ids: list[UUID]


class TaskResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    status: TaskStatus
    priority: Priority
    created_at: datetime
    completed_at: datetime | None = None
