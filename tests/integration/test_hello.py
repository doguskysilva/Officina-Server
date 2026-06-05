import pytest


@pytest.mark.asyncio
async def test_hello_endpoint(client):
    response = await client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["components"]["database"] == "ok"
