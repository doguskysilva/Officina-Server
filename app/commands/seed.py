from pathlib import Path

import app.repository.models  # noqa: F401 — registers models before create_all
from sqlmodel import SQLModel, create_engine

from app.config import settings
from app.domain.task import Priority
from app.repository.connection import get_repository, set_repository
from app.repository.sqlite import SQLiteProjectRepository


_PROJECTS = [
    {
        "name": "Mobile App Redesign",
        "tasks": [],
    },
    {
        "name": "Backend API v2",
        "tasks": [
            ("Define OpenAPI schema", Priority.HIGH, "done"),
            ("Set up authentication", Priority.HIGH, "done"),
            ("Implement rate limiting", Priority.MEDIUM, "done"),
            ("Write endpoint tests", Priority.HIGH, "pending"),
            ("Add pagination support", Priority.MEDIUM, "pending"),
            ("Integrate logging", Priority.LOW, "pending"),
            ("Performance benchmarks", Priority.MEDIUM, "pending"),
            ("Deploy to staging", Priority.HIGH, "pending"),
        ],
        "status": "in_progress",
    },
    {
        "name": "Data Pipeline Migration",
        "tasks": [
            ("Audit existing pipeline", Priority.HIGH, "done"),
            ("Map data sources", Priority.MEDIUM, "done"),
            ("Design new schema", Priority.HIGH, "pending"),
            ("Build ETL scripts", Priority.HIGH, "pending"),
            ("Validate data integrity", Priority.HIGH, "pending"),
            ("Switch production traffic", Priority.MEDIUM, "pending"),
        ],
        "status": "in_progress",
    },
    {
        "name": "Marketing Website Launch",
        "tasks": [
            ("Write copy for landing page", Priority.HIGH, "done"),
            ("Design hero section", Priority.HIGH, "done"),
            ("Implement responsive layout", Priority.MEDIUM, "done"),
            ("SEO meta tags", Priority.MEDIUM, "done"),
            ("Set up analytics", Priority.LOW, "done"),
            ("Cross-browser testing", Priority.MEDIUM, "done"),
            ("Deploy to CDN", Priority.HIGH, "done"),
        ],
        "status": "done",
    },
    {
        "name": "Legacy System Audit",
        "tasks": [
            ("Inventory all services", Priority.HIGH, "cancelled"),
            ("Document dependencies", Priority.MEDIUM, "cancelled"),
            ("Identify security gaps", Priority.HIGH, "pending"),
            ("Estimate migration cost", Priority.LOW, "pending"),
            ("Present findings to team", Priority.MEDIUM, "pending"),
        ],
        "status": "cancelled",
    },
]


def _seed(repo) -> None:
    for spec in _PROJECTS:
        project = repo.create_project(spec["name"])

        status = spec.get("status")

        if status in ("in_progress", "done", "cancelled"):
            project.start()

        done_ids = set()
        cancelled_ids = set()

        for title, priority, task_status in spec.get("tasks", []):
            task = project.add_task(title, priority)
            if task_status == "done":
                done_ids.add(task.id)
            elif task_status == "cancelled":
                cancelled_ids.add(task.id)

        if done_ids:
            project.complete_tasks(done_ids)
        if cancelled_ids:
            project.cancel_tasks(cancelled_ids)

        if status == "done":
            project.complete()
        elif status == "cancelled":
            project.cancel()

        repo.save_project(project)
        task_count = len(project.tasks)
        print(f"  {project.name} [{project.status}] — {task_count} task(s)")


def _ensure_db_dir(url: str) -> None:
    prefix = "sqlite:///"
    if url.startswith(prefix):
        path = Path(url[len(prefix):])
        if path.name:  # not :memory:
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                print(f"Error: cannot create database directory '{path.parent}'.")
                print("Set DATABASE_URL in your .env file, e.g.:")
                print("  DATABASE_URL=sqlite:///./dev.db")
                raise SystemExit(1)


def main() -> None:
    _ensure_db_dir(settings.database_url)
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    set_repository(SQLiteProjectRepository(engine))

    repo = get_repository()

    if repo.list_projects():
        print("Database already has projects — skipping seed.")
        return

    print("Seeding database...")
    _seed(repo)
    print("Done.")
