import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

import app.repository.models  # noqa: F401 — registers models before create_all
from app.main import app
from app.repository.connection import set_repository
from app.repository.sqlite import SQLiteProjectRepository


@pytest.fixture(autouse=True)
def setup_repository():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    set_repository(SQLiteProjectRepository(engine))
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
