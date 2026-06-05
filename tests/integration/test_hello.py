import pytest


@pytest.mark.asyncio
async def test_hello_endpoint(client):
    response = await client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
