from fastapi import FastAPI

from app.routers.projects import router as projects_router

app = FastAPI(title="OfficinaServer")

app.include_router(projects_router, prefix="/api")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/hello")
def hello() -> dict:
    return {"message": "Hello, World!"}
