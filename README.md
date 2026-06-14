# Officina Server

A REST API for managing projects and tasks, built with FastAPI and SQLite. Projects move through a simple state machine (`WAITING → IN_PROGRESS → DONE / CANCELLED`); tasks can only be created and mutated while their project is active.

![Python](https://img.shields.io/badge/python-3.14-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-green?logo=fastapi&logoColor=white)
![SQLModel](https://img.shields.io/badge/SQLModel-0.0.38+-orange)
![uv](https://img.shields.io/badge/uv-package%20manager-purple)
![Ruff](https://img.shields.io/badge/linter-ruff-red)

---

## What it does

Officina Server exposes a JSON HTTP API that lets you:

- Create and manage **projects** with a lifecycle state machine
- Add **tasks** (with priority) to in-progress projects
- Transition task status — complete or cancel individual tasks or all at once
- Finish a project only once all its tasks are completed
- Check service health including database connectivity

---

## Architecture

The project follows a small **hexagonal (ports and adapters)** style. HTTP concerns stay at
the edge, while application services receive their persistence dependency through the
`ProjectRepository` protocol:

```
routers  →  services  →  repository protocol
routers  →  adapters  →  ports / wire schemas
repository implementation  →  adapters  →  domain
```

| Layer | Path | Responsibility |
|---|---|---|
| `domain` | `app/domain/` | Core business logic — pure Python dataclasses, no framework imports |
| `ports` | `app/ports/` | Pydantic wire schemas (request/response shapes) |
| `adapters` | `app/adapters/` | Translate between domain entities and wire schemas / ORM models |
| `repository` | `app/repository/` | Repository protocol plus SQLite persistence via SQLModel |
| `services` | `app/services/` | Orchestration — fetch, guard, call domain method, save; raises application exceptions instead of HTTP exceptions |
| `routers` | `app/routers/` | HTTP boundary — route definitions, dependency wiring, and response shaping |

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | **3.14** | See `.python-version` |
| [uv](https://docs.astral.sh/uv/) | latest | Dependency management and script runner |

Install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Local setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd Officina-Server

# 2. Install all dependencies (including dev)
uv sync

# 3. Start the development server
uv run uvicorn app.main:app --reload
```

The API is now available at `http://localhost:8000`.

On first start, SQLModel creates the database tables automatically (`SQLModel.metadata.create_all`). No manual migration step is required.

---

## Environment variables

| Variable | Description | Default | Required |
|---|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string for SQLite | `sqlite:////app/data/officina.db` | No |

For local development, override the default Docker path:

```bash
# .env
DATABASE_URL=sqlite:///./dev.db
```

`pydantic-settings` reads from a `.env` file in the working directory automatically.

> There is no `.env.example` in the repository. Create `.env` manually if you need to override the default.

---

## Running the server

**Development (with auto-reload):**

```bash
uv run uvicorn app.main:app --reload
```

**Docker:**

```bash
docker compose up
```

This builds the image and starts the API on `http://localhost:8000`. The SQLite database is stored inside the container at `/app/data/officina.db` and is **not** persisted to a host volume by default.

To persist data across container restarts, add a volume to `docker-compose.yml`:

```yaml
volumes:
  - ./data:/app/data
```

---

## Tests

```bash
uv run pytest                                              # all tests
uv run pytest tests/unit                                   # unit tests only
uv run pytest tests/integration                            # integration tests only
uv run pytest tests/unit/domain                            # domain unit tests only
uv run pytest -k test_name                                 # single test by name
uv run pytest --cov=app --cov-report=term-missing          # with coverage
```

### Test structure

| Suite | Path | What it covers |
|---|---|---|
| Unit — domain | `tests/unit/domain/` | All `Project` and `Task` entity methods and properties |
| Unit — adapters | `tests/unit/adapters/` | Domain ↔ wire schema ↔ ORM model mapping |
| Unit — misc | `tests/unit/test_hello.py` | `hello()` function return value |
| Integration | `tests/integration/` | Full HTTP request/response cycle for all routes |

Integration tests use `httpx.AsyncClient` with `ASGITransport` (no real server or network socket) backed by a fresh `sqlite:///:memory:` database per test. Tests can seed state directly via `get_repository()` without going through HTTP — see `tests/seeds.py` for the available builders.

---

## API overview

Base URL: `/api` — no version prefix.

### Projects

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/projects` | List all projects. Optional `?sort=name_asc\|newest\|oldest` |
| `POST` | `/api/projects` | Create a project → `201` |
| `GET` | `/api/projects/{id}` | Get a single project |
| `DELETE` | `/api/projects/{id}` | Delete a project → `204` (blocked if `IN_PROGRESS`) |
| `POST` | `/api/projects/{id}/start` | Transition `WAITING → IN_PROGRESS` |
| `POST` | `/api/projects/{id}/finish` | Transition `IN_PROGRESS → DONE` (requires all tasks completed) |
| `POST` | `/api/projects/{id}/cancel` | Transition to `CANCELLED` (blocked if already `DONE`) |

### Tasks

All task routes are nested under a project. Task operations require the project to be `IN_PROGRESS`.

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/projects/{id}/tasks` | Add a task to the project → `201` |
| `PATCH` | `/api/projects/{id}/tasks/complete` | Complete specific tasks (body: `{task_ids: [...]}`) |
| `PATCH` | `/api/projects/{id}/tasks/cancel` | Cancel specific tasks (body: `{task_ids: [...]}`) |
| `PATCH` | `/api/projects/{id}/tasks/complete-all` | Complete all pending tasks |
| `DELETE` | `/api/projects/{id}/tasks` | Remove specific tasks (body: `{task_ids: [...]}`) |

### System

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | `{"status": "ok"\|"degraded", "components": {"database": "ok"\|"error"}}` |
| `GET` | `/hello` | `{"message": "Hello, World!"}` |

### Request / response shapes

**Create project:**
```json
POST /api/projects
{ "name": "My Project" }
```

**Project response:**
```json
{
  "id": "uuid",
  "name": "My Project",
  "status": "WAITING",
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": null,
  "tasks": [],
  "pending_count": 0,
  "can_finish": false,
  "is_active": false
}
```

**Add task:**
```json
POST /api/projects/{id}/tasks
{ "title": "Write tests", "priority": "HIGH" }
```

Valid `priority` values: `LOW`, `MEDIUM`, `HIGH`.

**Complete specific tasks:**
```json
PATCH /api/projects/{id}/tasks/complete
{ "task_ids": ["uuid-1", "uuid-2"] }
```

### State machine

**Project statuses:** `WAITING → IN_PROGRESS → DONE` or `WAITING → IN_PROGRESS → CANCELLED`

- A project can only be deleted when not `IN_PROGRESS`.
- A project can only be finished when it has at least one task and all tasks are completed (`can_finish`).
- A project cannot be cancelled once `DONE`.

**Task statuses:** `PENDING → DONE` or `PENDING → CANCELLED`

- Tasks can only be created and mutated while the project is `IN_PROGRESS`.

**Conflict errors (`409`)** are returned when a state transition is not permitted.

---

## Database

SQLite, managed by SQLModel (SQLAlchemy).

**Schema is created automatically** on startup via `SQLModel.metadata.create_all(engine)`. There are no migration files — the schema is defined in code in `app/repository/models.py`.

**Tables:**

| Table | Description |
|---|---|
| `project` | One row per project, indexed on `name` |
| `task` | One row per task, foreign key to `project.id`, indexed on `project_id` |

The default database path inside Docker is `/app/data/officina.db`. Override with the `DATABASE_URL` environment variable.

---

## Linting and formatting

```bash
uv run ruff check --fix .    # lint with auto-fix
uv run ruff format .         # format
```

Line length: 100. Target: Python 3.14. Enabled rule sets: `E`, `F`, `I` (isort), `UP` (pyupgrade).

---

## Folder structure

```
app/
├── config.py           # Settings — reads DATABASE_URL from environment / .env
├── main.py             # FastAPI app, lifespan (DB init), health + hello routes
├── domain/
│   ├── project.py      # Project dataclass + ProjectStatus enum
│   └── task.py         # Task dataclass + TaskStatus + Priority enums
├── ports/
│   ├── project_wire.py # ProjectCreate (request) + ProjectResponse (response)
│   └── task_wire.py    # TaskCreate, TaskIdsRequest, TaskResponse
├── adapters/
│   ├── datetime_adapter.py   # to_naive() / to_aware() — SQLite ↔ UTC-aware datetimes
│   ├── project_adapter.py    # domain ↔ wire schema ↔ SQLModel model
│   └── task_adapter.py       # domain ↔ wire schema ↔ SQLModel model
├── repository/
│   ├── base.py         # ProjectRepository Protocol (interface)
│   ├── connection.py   # get_repository() / set_repository() singleton
│   ├── models.py       # ProjectModel + TaskModel SQLModel table classes
│   └── sqlite.py       # SQLiteProjectRepository — concrete SQLite implementation
├── services/
│   ├── project_service.py    # CRUD + state transitions for projects
│   └── task_service.py       # add / complete / cancel / remove tasks
└── routers/
    └── projects.py     # All HTTP routes (projects + nested task routes)

tests/
├── conftest.py         # Fixtures: in-memory DB per test, async HTTP client
├── seeds.py            # Domain builders + DB seeders for test setup
├── integration/        # Full HTTP integration tests (httpx + ASGITransport)
└── unit/
    ├── adapters/        # Adapter mapping unit tests
    └── domain/          # Domain entity behaviour unit tests
```

---

## Deployment

The `Dockerfile` uses a two-stage build:

1. **Builder** — installs `uv`, syncs production dependencies into `.venv`
2. **Runtime** — copies only `.venv` and `app/`, runs as non-root user `appuser`

The image exposes port `8000`. The default `CMD` runs Uvicorn bound to `0.0.0.0`.

```bash
# Build
docker build -t officinaserver .

# Run
docker run -p 8000:8000 officinaserver

# Or with docker compose
docker compose up
```

> No CI/CD pipelines are currently configured. <!-- TODO: fill in -->

---

## Contributing

- Match the hexagonal architecture: outer layers import from inner layers, never the reverse.
- Domain entities own all state mutations — services call domain methods and persist; they do not set attributes directly.
- Port schemas contain no logic — computed fields (e.g. `pending_count`, `can_finish`) are plain scalars populated by the adapter, not derived inside the schema.
- `app/repository/models.py` is internal to the repository layer — do not import SQLModel table classes outside of `repository/`.
- Add unit tests in `tests/unit/` for new domain and adapter logic, and integration tests in `tests/integration/` for new routes.
- Run `uv run ruff check --fix . && uv run ruff format .` before committing.
- Run `uv run pytest` and confirm all tests pass before opening a pull request.
