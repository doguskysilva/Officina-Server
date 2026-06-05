from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class Priority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class Task:
    id: UUID
    project_id: UUID
    title: str
    status: TaskStatus
    priority: Priority
    created_at: datetime
    completed_at: datetime | None = None

    def complete(self) -> None:
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now(UTC)

    def cancel(self) -> None:
        self.status = TaskStatus.CANCELLED
