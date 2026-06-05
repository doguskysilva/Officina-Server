# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run through `uv run`:

```bash
uv run uvicorn app.main:app --reload   # dev server at localhost:8000
uv run pytest                          # all tests
uv run pytest tests/unit               # unit tests only
uv run pytest tests/integration        # integration tests only
uv run pytest tests/unit/domain        # domain unit tests only
uv run pytest -k test_name             # single test by name
uv run pytest --cov=app --cov-report=term-missing  # with coverage
uv run ruff check --fix .              # lint + auto-fix
uv run ruff format .                   # format
```

## Architecture

This project follows **hexagonal (ports and adapters)** architecture. The dependency flow is strictly one-directional — outer layers import from inner layers, never the reverse.

```
domain  ←  repository
domain  ←  services  ←  routers
domain  ←  adapters  ←  routers
ports   ←  adapters  ←  routers
```

### Layers

**`app/domain/`** — Core business logic. No framework imports. Enums live alongside their entity (`ProjectStatus` in `project.py`, `TaskStatus`/`Priority` in `task.py`). Domain entities own all state mutations via explicit methods (`project.start()`, `project.complete()`, `project.cancel()`, `project.add_task()`, etc.). Services never set attributes directly on domain objects.

**`app/ports/`** — Pure Pydantic wire schemas with no logic. `project_wire.py` holds both `ProjectCreate` (request) and `ProjectResponse` (response). Computed fields (`pending_count`, `can_finish`, `is_active`) are plain `int`/`bool` fields — populated by the adapter, not derived inside the schema.

**`app/adapters/`** — Translate between domain entities and wire schemas. `project_adapter.record_to_response()` explicitly maps domain properties onto the flat response schema. `project_adapter.from_create_request()` extracts the name from the create request.

**`app/repository/`** — SQLite persistence via SQLModel (`sqlite.py`). `base.py` defines the `ProjectRepository` Protocol. `connection.py` holds the active repository instance (`get_repository()` / `set_repository()`); must be initialised before use (done in `main.py` lifespan and in `tests/conftest.py`). `models.py` defines `ProjectModel`/`TaskModel` SQLModel table classes — never imported outside the repository layer.

**`app/services/`** — Orchestration only. Fetch the entity, check domain properties (`project.can_start`, `project.can_finish`, etc.), raise `HTTPException` on violations, call the domain method, save. Services have no business logic of their own.

**`app/routers/`** — HTTP boundary. All task endpoints live in `routers/projects.py` as nested routes under `/{id}/tasks`. Path parameters use `id` (not `project_id`) since the router prefix already provides context.

### API

Base URL: `/api` — no version prefix by design.

All project endpoints: `GET/POST /api/projects`, `GET/DELETE /api/projects/{id}`, `POST /api/projects/{id}/start|finish|cancel`, and task sub-routes under `/api/projects/{id}/tasks`.

### Tests

Integration tests use `httpx.AsyncClient` with `ASGITransport` — no real server needed. `tests/conftest.py` spins up a fresh `sqlite:///:memory:` database with `StaticPool` before each test and tears it down after, providing full isolation. Tests can seed state directly via `get_repository()` without going through HTTP. The `_active_project` helper in `test_tasks.py` creates and starts a project in one step (task operations require `IN_PROGRESS`).

Unit tests are split: `tests/unit/domain/` for domain entity behaviour, `tests/unit/adapters/` for adapter mapping.
