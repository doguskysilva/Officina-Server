from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.exceptions import InvalidProjectOperation
from app.domain.task import Priority, Task, TaskStatus


class ProjectStatus(StrEnum):
    WAITING = "WAITING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


@dataclass
class Project:
    id: UUID
    name: str
    status: ProjectStatus
    created_at: datetime
    completed_at: datetime | None = None
    tasks: list[Task] = field(default_factory=list)

    @classmethod
    def create(cls, name: str) -> Project:
        return cls(
            id=uuid4(),
            name=name,
            status=ProjectStatus.WAITING,
            created_at=datetime.now(UTC),
        )

    @property
    def pending_count(self) -> int:
        return sum(1 for t in self.tasks if t.status == TaskStatus.PENDING)

    @property
    def can_finish(self) -> bool:
        return len(self.tasks) > 0 and self.pending_count == 0

    @property
    def is_active(self) -> bool:
        return self.status == ProjectStatus.IN_PROGRESS

    @property
    def can_start(self) -> bool:
        return self.status == ProjectStatus.WAITING

    @property
    def can_be_deleted(self) -> bool:
        return self.status != ProjectStatus.IN_PROGRESS

    @property
    def can_cancel(self) -> bool:
        return self.status != ProjectStatus.DONE

    def ensure_can_be_deleted(self) -> None:
        if not self.can_be_deleted:
            raise InvalidProjectOperation("Cannot delete an IN_PROGRESS project")

    def start(self) -> None:
        if not self.can_start:
            raise InvalidProjectOperation("Project must be WAITING to start")
        self.status = ProjectStatus.IN_PROGRESS

    def complete(self) -> None:
        if not self.is_active:
            raise InvalidProjectOperation("Project must be IN_PROGRESS to finish")
        if not self.can_finish:
            raise InvalidProjectOperation("Project has pending tasks or no tasks")
        self.status = ProjectStatus.DONE
        self.completed_at = datetime.now(UTC)

    def cancel(self) -> None:
        if not self.can_cancel:
            raise InvalidProjectOperation("Cannot cancel a DONE project")
        self.status = ProjectStatus.CANCELLED

    def add_task(self, title: str, priority: Priority) -> Task:
        self._ensure_active("Project must be IN_PROGRESS to add tasks")
        task = Task(
            id=uuid4(),
            project_id=self.id,
            title=title,
            status=TaskStatus.PENDING,
            priority=priority,
            created_at=datetime.now(UTC),
        )
        self.tasks.append(task)
        return task

    def complete_tasks(self, task_ids: set[UUID]) -> None:
        self._ensure_active("Project must be IN_PROGRESS to complete tasks")
        for task in self.tasks:
            if task.id in task_ids:
                task.complete()

    def cancel_tasks(self, task_ids: set[UUID]) -> None:
        self._ensure_active("Project must be IN_PROGRESS to cancel tasks")
        for task in self.tasks:
            if task.id in task_ids:
                task.cancel()

    def complete_all_tasks(self) -> None:
        self._ensure_active("Project must be IN_PROGRESS to complete tasks")
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                task.complete()

    def remove_tasks(self, task_ids: set[UUID]) -> None:
        self._ensure_active("Project must be IN_PROGRESS to remove tasks")
        self.tasks = [t for t in self.tasks if t.id not in task_ids]

    def _ensure_active(self, message: str) -> None:
        if not self.is_active:
            raise InvalidProjectOperation(message)


@dataclass(frozen=True)
class ProjectSummary:
    id: UUID
    name: str
    status: ProjectStatus
    created_at: datetime
    completed_at: datetime | None
    pending_count: int
    can_finish: bool
    is_active: bool
