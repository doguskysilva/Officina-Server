from uuid import uuid4

import pytest

from tests.factories import ProjectFactory, TaskFactory
from tests.seeds import seed_project, seed_projects


@pytest.mark.asyncio
async def test_list_projects_empty(client):
    response = await client.get("/api/projects")
    data = response.json()

    assert response.status_code == 200
    assert data == []


@pytest.mark.asyncio
async def test_create_project(client):
    response = await client.post("/api/projects", json={"name": "App Mobile"})
    data = response.json()

    assert response.status_code == 201
    assert data["name"] == "App Mobile"
    assert data["status"] == "WAITING"
    assert data["tasks"] == []
    assert data["pending_count"] == 0
    assert data["can_finish"] is False
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_get_project(client):
    project = ProjectFactory()
    seed_project(project)

    response = await client.get(f"/api/projects/{project.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == str(project.id)
    assert data["name"] == project.name


@pytest.mark.asyncio
async def test_get_project_not_found(client):
    response = await client.get(f"/api/projects/{uuid4()}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project(client):
    project = ProjectFactory()
    seed_project(project)

    delete_response = await client.delete(f"/api/projects/{project.id}")
    get_response = await client.get(f"/api/projects/{project.id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_in_progress_project_fails(client):
    project = ProjectFactory(in_progress=True)
    seed_project(project)

    response = await client.delete(f"/api/projects/{project.id}")

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_start_project(client):
    project = ProjectFactory()
    seed_project(project)

    response = await client.post(f"/api/projects/{project.id}/start")
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "IN_PROGRESS"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_start_already_started_fails(client):
    project = ProjectFactory(in_progress=True)
    seed_project(project)

    response = await client.post(f"/api/projects/{project.id}/start")

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_cancel_project(client):
    project = ProjectFactory()
    seed_project(project)

    response = await client.post(f"/api/projects/{project.id}/cancel")
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_finish_project_not_in_progress_fails(client):
    project = ProjectFactory()
    seed_project(project)

    response = await client.post(f"/api/projects/{project.id}/finish")

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_finish_project_no_tasks_fails(client):
    project = ProjectFactory(in_progress=True)
    seed_project(project)

    response = await client.post(f"/api/projects/{project.id}/finish")

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_finish_project_succeeds(client):
    project = ProjectFactory(in_progress=True)
    task = TaskFactory(done=True, project_id=project.id)
    project.tasks = [task]
    seed_project(project)

    response = await client.post(f"/api/projects/{project.id}/finish")
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "DONE"
    assert data["completed_at"] is not None


@pytest.mark.asyncio
async def test_cancel_done_project_fails(client):
    project = ProjectFactory(done=True)
    task = TaskFactory(done=True, project_id=project.id)
    project.tasks = [task]
    seed_project(project)

    response = await client.post(f"/api/projects/{project.id}/cancel")

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_projects_sorted_by_name(client):
    seed_projects(ProjectFactory(name="Zebra"), ProjectFactory(name="Alpha"))

    response = await client.get("/api/projects?sort=name_asc")
    data = response.json()

    assert response.status_code == 200
    assert [p["name"] for p in data] == ["Alpha", "Zebra"]


@pytest.mark.asyncio
async def test_list_projects_sorted_newest(client):
    seed_projects(ProjectFactory(name="First"), ProjectFactory(name="Second"))

    response = await client.get("/api/projects?sort=newest")
    data = response.json()

    assert response.status_code == 200
    assert data[0]["name"] == "Second"


@pytest.mark.asyncio
async def test_list_projects_sorted_oldest(client):
    seed_projects(ProjectFactory(name="First"), ProjectFactory(name="Second"))

    response = await client.get("/api/projects?sort=oldest")
    data = response.json()

    assert response.status_code == 200
    assert data[0]["name"] == "First"
