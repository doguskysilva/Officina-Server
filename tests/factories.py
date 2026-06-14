import random
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
    status = factory.LazyFunction(lambda: random.choice(list(TaskStatus)))
    priority = factory.LazyFunction(lambda: random.choice(list(Priority)))
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    completed_at = None

    class Params:
        pending = factory.Trait(status=TaskStatus.PENDING)
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
    status = factory.LazyFunction(lambda: random.choice(list(ProjectStatus)))
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    completed_at = None
    tasks = factory.LazyFunction(list)

    class Params:
        waiting = factory.Trait(status=ProjectStatus.WAITING)
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
    status = factory.LazyFunction(lambda: random.choice([s.value for s in TaskStatus]))
    priority = factory.LazyFunction(lambda: random.choice([p.value for p in Priority]))
    created_at = factory.LazyFunction(datetime.now)  # naive — no tz, mirrors SQLite storage
    completed_at = None

    class Params:
        pending = factory.Trait(status="PENDING")
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
    status = factory.LazyFunction(lambda: random.choice([s.value for s in ProjectStatus]))
    created_at = factory.LazyFunction(datetime.now)  # naive — no tz, mirrors SQLite storage
    completed_at = None

    @factory.post_generation
    def tasks(obj, create, extracted, **kwargs):
        obj.tasks = extracted if extracted is not None else []

    class Params:
        waiting = factory.Trait(status="WAITING")
        done = factory.Trait(
            status="DONE",
            completed_at=factory.LazyFunction(datetime.now),
        )
