import pytest

from app.domain.task import Priority
from tests.seeds import (
    active_project,
    active_project_with_done_task,
    active_project_with_task,
    active_project_with_tasks,
    seed_project,
    waiting_project,
)

# --- POST /projects/{id}/tasks ---


@pytest.mark.asyncio
async def test_add_task(client):
    project = active_project()
    seed_project(project)

    response = await client.post(
        f"/api/projects/{project.id}/tasks",
        json={"title": "Write tests", "priority": "HIGH"},
    )
    data = response.json()

    assert response.status_code == 201
    assert data["title"] == "Write tests"
    assert data["priority"] == "HIGH"
    assert data["status"] == "PENDING"
    assert data["project_id"] == str(project.id)


@pytest.mark.asyncio
async def test_add_task_to_non_active_project_fails(client):
    project = waiting_project()
    seed_project(project)

    response = await client.post(
        f"/api/projects/{project.id}/tasks",
        json={"title": "Task", "priority": "LOW"},
    )

    assert response.status_code == 409


# --- PATCH /projects/{id}/tasks/complete ---


@pytest.mark.asyncio
async def test_complete_tasks_on_non_active_project_fails(client):
    project = waiting_project()
    seed_project(project)

    response = await client.patch(
        f"/api/projects/{project.id}/tasks/complete",
        json={"task_ids": []},
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_complete_tasks(client):
    project, task = active_project_with_task("Do it", Priority.MEDIUM)
    seed_project(project)

    response = await client.patch(
        f"/api/projects/{project.id}/tasks/complete",
        json={"task_ids": [str(task.id)]},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["tasks"][0]["status"] == "DONE"
    assert data["tasks"][0]["completed_at"] is not None


# --- PATCH /projects/{id}/tasks/cancel ---


@pytest.mark.asyncio
async def test_cancel_tasks_on_non_active_project_fails(client):
    project = waiting_project()
    seed_project(project)

    response = await client.patch(
        f"/api/projects/{project.id}/tasks/cancel",
        json={"task_ids": []},
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_cancel_tasks(client):
    project, task = active_project_with_task("Drop it", Priority.LOW)
    seed_project(project)

    response = await client.patch(
        f"/api/projects/{project.id}/tasks/cancel",
        json={"task_ids": [str(task.id)]},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["tasks"][0]["status"] == "CANCELLED"


# --- PATCH /projects/{id}/tasks/complete-all ---


@pytest.mark.asyncio
async def test_complete_all_tasks_on_non_active_project_fails(client):
    project = waiting_project()
    seed_project(project)

    response = await client.patch(f"/api/projects/{project.id}/tasks/complete-all")

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_complete_all_tasks(client):
    project = active_project_with_tasks(3)
    seed_project(project)

    response = await client.patch(f"/api/projects/{project.id}/tasks/complete-all")
    data = response.json()

    assert response.status_code == 200
    assert all(t["status"] == "DONE" for t in data["tasks"])


# --- DELETE /projects/{id}/tasks ---


@pytest.mark.asyncio
async def test_remove_tasks_on_non_active_project_fails(client):
    project = waiting_project()
    seed_project(project)

    response = await client.request(
        "DELETE",
        f"/api/projects/{project.id}/tasks",
        json={"task_ids": []},
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_remove_tasks(client):
    project, task = active_project_with_task("Remove me", Priority.LOW)
    seed_project(project)

    response = await client.request(
        "DELETE",
        f"/api/projects/{project.id}/tasks",
        json={"task_ids": [str(task.id)]},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["tasks"] == []


# --- finish (via seed with done task) ---


@pytest.mark.asyncio
async def test_finish_project_via_seed(client):
    project, _ = active_project_with_done_task()
    seed_project(project)

    response = await client.post(f"/api/projects/{project.id}/finish")
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "DONE"
    assert data["completed_at"] is not None
