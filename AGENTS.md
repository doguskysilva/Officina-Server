# AGENTS.md

This file provides guidance to coding agents (including GitHub Copilot) when working with code in this repository.

## Commands

Run all project commands through `uv run`:

```bash
uv run uvicorn app.main:app --reload                    # dev server at localhost:8000
uv run pytest                                           # all tests
uv run pytest tests/unit                                # unit tests only
uv run pytest tests/integration                         # integration tests only
uv run pytest tests/unit/domain                         # domain unit tests only
uv run pytest -k test_name                              # single test by name
uv run pytest --cov=app --cov-report=term-missing      # with coverage
uv run ruff check --fix .                               # lint + auto-fix
uv run ruff format .                                    # format
```

## Architecture

This project uses **hexagonal (ports and adapters)** architecture.
Dependencies are one-directional: outer layers may import inner layers, never the reverse.

```text
domain  ←  repository
domain  ←  services  ←  routers
domain  ←  adapters  ←  routers
ports   ←  adapters  ←  routers
```

### Layer responsibilities

**`app/domain/`**  
Core business logic only (no framework imports). Enums live with their entities (`ProjectStatus` in `project.py`, `TaskStatus`/`Priority` in `task.py`). Domain entities own state transitions via explicit methods (`project.start()`, `project.complete()`, `project.cancel()`, `project.add_task()`, etc.). Services must not mutate domain attributes directly.

**`app/ports/`**  
Pure Pydantic wire schemas without business logic. `project_wire.py` contains both `ProjectCreate` (request) and `ProjectResponse` (response). Computed API fields (`pending_count`, `can_finish`, `is_active`) are plain `int`/`bool` values populated by adapters.

**`app/adapters/`**  
Translation between domain entities and wire schemas. `project_adapter.record_to_response()` maps domain fields to the flat response schema. `project_adapter.from_create_request()` extracts the project name from the create request.

**`app/repository/`**  
SQLite persistence via SQLModel (`sqlite.py`). `base.py` defines the `ProjectRepository` protocol. `connection.py` stores the active repository (`get_repository()`/`set_repository()`), initialized in app lifespan (`main.py`) and in tests (`tests/conftest.py`). `models.py` defines `ProjectModel`/`TaskModel`; do not import these outside the repository layer.

**`app/services/`**  
Application orchestration only. Fetch entities, enforce domain property guards (`project.can_start`, `project.can_finish`, etc.), raise `HTTPException` for rule violations, call domain methods, then persist. Keep business rules in domain objects.

**`app/routers/`**  
HTTP boundary. Task endpoints are nested in `routers/projects.py` under `/{id}/tasks`. Use path parameter name `id` (not `project_id`) because the router prefix already conveys project context.

## API

Base URL is `/api` (no version prefix).

Project routes:
- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/{id}`
- `DELETE /api/projects/{id}`
- `POST /api/projects/{id}/start`
- `POST /api/projects/{id}/finish`
- `POST /api/projects/{id}/cancel`
- Task sub-routes under `/api/projects/{id}/tasks`

## Tests

Integration tests use `httpx.AsyncClient` with `ASGITransport` (no live server). `tests/conftest.py` creates a fresh in-memory SQLite DB (`sqlite:///:memory:` with `StaticPool`) per test for isolation. Tests may seed state directly through `get_repository()` when appropriate. In `test_tasks.py`, `_active_project` creates and starts a project, since task operations require `IN_PROGRESS`.

Unit tests are split by concern:
- `tests/unit/domain/` for domain behavior
- `tests/unit/adapters/` for adapter mapping
