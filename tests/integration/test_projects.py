import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.repository.in_memory import repo


@pytest.fixture(autouse=True)
def reset_repo():
    repo._projects.clear()


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


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
    project_id = (await client.post("/api/projects", json={"name": "My Project"})).json()["id"]

    response = await client.get(f"/api/projects/{project_id}")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == project_id


@pytest.mark.asyncio
async def test_get_project_not_found(client):
    response = await client.get("/api/projects/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project(client):
    project_id = (await client.post("/api/projects", json={"name": "To Delete"})).json()["id"]

    delete_response = await client.delete(f"/api/projects/{project_id}")
    get_response = await client.get(f"/api/projects/{project_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_in_progress_project_fails(client):
    project_id = (await client.post("/api/projects", json={"name": "Active"})).json()["id"]
    await client.post(f"/api/projects/{project_id}/start")

    response = await client.delete(f"/api/projects/{project_id}")

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_start_project(client):
    project_id = (await client.post("/api/projects", json={"name": "Sprint 1"})).json()["id"]

    response = await client.post(f"/api/projects/{project_id}/start")
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "IN_PROGRESS"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_start_already_started_fails(client):
    project_id = (await client.post("/api/projects", json={"name": "Sprint"})).json()["id"]
    await client.post(f"/api/projects/{project_id}/start")

    response = await client.post(f"/api/projects/{project_id}/start")

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_cancel_project(client):
    project_id = (await client.post("/api/projects", json={"name": "Drop this"})).json()["id"]

    response = await client.post(f"/api/projects/{project_id}/cancel")
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_finish_project_no_tasks_fails(client):
    project_id = (await client.post("/api/projects", json={"name": "Empty"})).json()["id"]
    await client.post(f"/api/projects/{project_id}/start")

    response = await client.post(f"/api/projects/{project_id}/finish")

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_projects_sorted_by_name(client):
    await client.post("/api/projects", json={"name": "Zebra"})
    await client.post("/api/projects", json={"name": "Alpha"})

    response = await client.get("/api/projects?sort=name_asc")
    data = response.json()

    assert response.status_code == 200
    assert [p["name"] for p in data] == ["Alpha", "Zebra"]


@pytest.mark.asyncio
async def test_list_projects_sorted_newest(client):
    await client.post("/api/projects", json={"name": "First"})
    await client.post("/api/projects", json={"name": "Second"})

    response = await client.get("/api/projects?sort=newest")
    data = response.json()

    assert response.status_code == 200
    assert data[0]["name"] == "Second"


@pytest.mark.asyncio
async def test_list_projects_sorted_oldest(client):
    await client.post("/api/projects", json={"name": "First"})
    await client.post("/api/projects", json={"name": "Second"})

    response = await client.get("/api/projects?sort=oldest")
    data = response.json()

    assert response.status_code == 200
    assert data[0]["name"] == "First"


@pytest.mark.asyncio
async def test_finish_project_not_in_progress_fails(client):
    project_id = (await client.post("/api/projects", json={"name": "Waiting"})).json()["id"]

    response = await client.post(f"/api/projects/{project_id}/finish")

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_finish_project_succeeds(client):
    project_id = (await client.post("/api/projects", json={"name": "Sprint"})).json()["id"]
    await client.post(f"/api/projects/{project_id}/start")
    task = (await client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Last task", "priority": "HIGH"},
    )).json()
    await client.patch(
        f"/api/projects/{project_id}/tasks/complete",
        json={"task_ids": [task["id"]]},
    )

    response = await client.post(f"/api/projects/{project_id}/finish")
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "DONE"
    assert data["completed_at"] is not None


@pytest.mark.asyncio
async def test_cancel_done_project_fails(client):
    project_id = (await client.post("/api/projects", json={"name": "Sprint"})).json()["id"]
    await client.post(f"/api/projects/{project_id}/start")
    task = (await client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Last task", "priority": "HIGH"},
    )).json()
    await client.patch(
        f"/api/projects/{project_id}/tasks/complete",
        json={"task_ids": [task["id"]]},
    )
    await client.post(f"/api/projects/{project_id}/finish")

    response = await client.post(f"/api/projects/{project_id}/cancel")

    assert response.status_code == 409
