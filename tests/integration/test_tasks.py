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


async def _active_project(client: AsyncClient) -> dict:
    project = (await client.post("/api/projects", json={"name": "Sprint"})).json()
    return (await client.post(f"/api/projects/{project['id']}/start")).json()


# --- POST /projects/{id}/tasks ---


@pytest.mark.asyncio
async def test_add_task(client):
    project = await _active_project(client)

    response = await client.post(
        f"/api/projects/{project['id']}/tasks",
        json={"title": "Write tests", "priority": "HIGH"},
    )
    data = response.json()

    assert response.status_code == 201
    assert data["title"] == "Write tests"
    assert data["priority"] == "HIGH"
    assert data["status"] == "PENDING"
    assert data["project_id"] == project["id"]


@pytest.mark.asyncio
async def test_add_task_to_non_active_project_fails(client):
    project = (await client.post("/api/projects", json={"name": "Waiting"})).json()

    response = await client.post(
        f"/api/projects/{project['id']}/tasks",
        json={"title": "Task", "priority": "LOW"},
    )

    assert response.status_code == 409


# --- PATCH /projects/{id}/tasks/complete ---


@pytest.mark.asyncio
async def test_complete_tasks_on_non_active_project_fails(client):
    project_id = (await client.post("/api/projects", json={"name": "Waiting"})).json()["id"]

    response = await client.patch(
        f"/api/projects/{project_id}/tasks/complete",
        json={"task_ids": []},
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_complete_tasks(client):
    project = await _active_project(client)
    task = (
        await client.post(
            f"/api/projects/{project['id']}/tasks",
            json={"title": "Do it", "priority": "MEDIUM"},
        )
    ).json()

    response = await client.patch(
        f"/api/projects/{project['id']}/tasks/complete",
        json={"task_ids": [task["id"]]},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["tasks"][0]["status"] == "DONE"
    assert data["tasks"][0]["completed_at"] is not None


# --- PATCH /projects/{id}/tasks/cancel ---


@pytest.mark.asyncio
async def test_cancel_tasks_on_non_active_project_fails(client):
    project_id = (await client.post("/api/projects", json={"name": "Waiting"})).json()["id"]

    response = await client.patch(
        f"/api/projects/{project_id}/tasks/cancel",
        json={"task_ids": []},
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_cancel_tasks(client):
    project = await _active_project(client)
    task = (
        await client.post(
            f"/api/projects/{project['id']}/tasks",
            json={"title": "Drop it", "priority": "LOW"},
        )
    ).json()

    response = await client.patch(
        f"/api/projects/{project['id']}/tasks/cancel",
        json={"task_ids": [task["id"]]},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["tasks"][0]["status"] == "CANCELLED"


# --- PATCH /projects/{id}/tasks/complete-all ---


@pytest.mark.asyncio
async def test_complete_all_tasks_on_non_active_project_fails(client):
    project_id = (await client.post("/api/projects", json={"name": "Waiting"})).json()["id"]

    response = await client.patch(f"/api/projects/{project_id}/tasks/complete-all")

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_complete_all_tasks(client):
    project = await _active_project(client)
    for title in ("Task A", "Task B", "Task C"):
        await client.post(
            f"/api/projects/{project['id']}/tasks",
            json={"title": title, "priority": "MEDIUM"},
        )

    response = await client.patch(f"/api/projects/{project['id']}/tasks/complete-all")
    data = response.json()

    assert response.status_code == 200
    assert all(t["status"] == "DONE" for t in data["tasks"])


# --- DELETE /projects/{id}/tasks ---


@pytest.mark.asyncio
async def test_remove_tasks_on_non_active_project_fails(client):
    project_id = (await client.post("/api/projects", json={"name": "Waiting"})).json()["id"]

    response = await client.request(
        "DELETE",
        f"/api/projects/{project_id}/tasks",
        json={"task_ids": []},
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_remove_tasks(client):
    project = await _active_project(client)
    task = (
        await client.post(
            f"/api/projects/{project['id']}/tasks",
            json={"title": "Remove me", "priority": "LOW"},
        )
    ).json()

    response = await client.request(
        "DELETE",
        f"/api/projects/{project['id']}/tasks",
        json={"task_ids": [task["id"]]},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["tasks"] == []

