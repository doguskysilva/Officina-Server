from app.domain.project import ProjectStatus
from app.domain.task import Priority, TaskStatus
from tests.factories import ProjectFactory, TaskFactory


def test_factories_generate_random_data_with_traits():
    # trait fixes the target field; all other attributes are randomly generated
    p1 = ProjectFactory(in_progress=True)
    p2 = ProjectFactory(in_progress=True)

    assert p1.status == p2.status == ProjectStatus.IN_PROGRESS
    assert p1.id != p2.id
    assert p1.name != p2.name

    # task trait + direct override coexist
    t1 = TaskFactory(done=True, project_id=p1.id)
    t2 = TaskFactory(high_priority=True, project_id=p1.id)

    assert t1.status == TaskStatus.DONE
    assert t1.completed_at is not None
    assert t1.project_id == p1.id

    assert t2.status == TaskStatus.PENDING
    assert t2.priority == Priority.HIGH
    assert t1.id != t2.id
