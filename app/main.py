from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine

import app.repository.models  # noqa: F401 — registers models in SQLModel metadata
from app.config import settings
from app.repository.connection import set_repository
from app.repository.sqlite import SQLiteProjectRepository
from app.routers.projects import router as projects_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    set_repository(SQLiteProjectRepository(engine))
    yield
    engine.dispose()


app = FastAPI(title="OfficinaServer", lifespan=lifespan)

app.include_router(projects_router, prefix="/api")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/hello")
def hello() -> dict:
    return {"message": "Hello, World!"}
