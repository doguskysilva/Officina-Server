from datetime import UTC, datetime
from uuid import uuid4

import factory

from app.domain.project import Project, ProjectStatus
from app.domain.task import Priority, Task, TaskStatus
from app.repository.models import ProjectModel, TaskModel


class TaskFactory(factory.Factory):
    class Meta:
        model = Task

    id = factory.LazyFunction(uuid4)
    project_id = factory.LazyFunction(uuid4)
    title = factory.Faker("sentence", nb_words=4)
    status = TaskStatus.PENDING
    priority = factory.Iterator([Priority.LOW, Priority.MEDIUM, Priority.HIGH])
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    completed_at = None

    class Params:
        done = factory.Trait(
            status=TaskStatus.DONE,
            completed_at=factory.LazyFunction(lambda: datetime.now(UTC)),
        )
        cancelled = factory.Trait(status=TaskStatus.CANCELLED)
        high_priority = factory.Trait(priority=Priority.HIGH)


class ProjectFactory(factory.Factory):
    class Meta:
        model = Project

    id = factory.LazyFunction(uuid4)
    name = factory.Faker("company")
    status = ProjectStatus.WAITING
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    completed_at = None
    tasks = factory.LazyFunction(list)

    class Params:
        in_progress = factory.Trait(status=ProjectStatus.IN_PROGRESS)
        done = factory.Trait(
            status=ProjectStatus.DONE,
            completed_at=factory.LazyFunction(lambda: datetime.now(UTC)),
        )
        cancelled = factory.Trait(status=ProjectStatus.CANCELLED)


class TaskModelFactory(factory.Factory):
    class Meta:
        model = TaskModel

    id = factory.LazyFunction(uuid4)
    project_id = factory.LazyFunction(uuid4)
    title = factory.Faker("sentence", nb_words=4)
    status = "PENDING"
    priority = "MEDIUM"
    created_at = factory.LazyFunction(datetime.now)  # naive — no tz, mirrors SQLite storage
    completed_at = None

    class Params:
        done = factory.Trait(
            status="DONE",
            completed_at=factory.LazyFunction(datetime.now),
        )
        cancelled = factory.Trait(status="CANCELLED")


class ProjectModelFactory(factory.Factory):
    class Meta:
        model = ProjectModel

    id = factory.LazyFunction(uuid4)
    name = factory.Faker("company")
    status = "WAITING"
    created_at = factory.LazyFunction(datetime.now)  # naive — no tz, mirrors SQLite storage
    completed_at = None

    @factory.post_generation
    def tasks(obj, create, extracted, **kwargs):
        obj.tasks = extracted if extracted is not None else []

    class Params:
        done = factory.Trait(
            status="DONE",
            completed_at=factory.LazyFunction(datetime.now),
        )
