from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, create_engine

import app.repository.models  # noqa: F401 — registers models in SQLModel metadata
from app.config import settings
from app.repository.connection import get_repository, set_repository
from app.repository.sqlite import SQLiteProjectRepository
from app.routers.projects import router as projects_router
from app.services.exceptions import ProjectConflict, ProjectNotFound


@asynccontextmanager
async def lifespan(_: FastAPI):
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    set_repository(SQLiteProjectRepository(engine))
    yield
    engine.dispose()


app = FastAPI(title="OfficinaServer", lifespan=lifespan)

app.include_router(projects_router, prefix="/api")


@app.exception_handler(ProjectNotFound)
async def project_not_found_handler(_, exc: ProjectNotFound) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ProjectConflict)
async def project_conflict_handler(_, exc: ProjectConflict) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.get("/health")
def health() -> JSONResponse:
    db_ok = get_repository().ping()
    components = {"database": "ok" if db_ok else "error"}
    status = "ok" if db_ok else "degraded"
    return JSONResponse(
        status_code=200 if status == "ok" else 503,
        content={"status": status, "components": components},
    )


@app.get("/hello")
def hello() -> dict:
    return {"message": "Hello, World!"}
