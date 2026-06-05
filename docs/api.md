# Officina API — Especificação REST

Stack: **FastAPI · Python 3.14 · uvicorn**  
Base URL: `http://localhost:8000/api`

---

## Modelos de domínio

Espelham exatamente os modelos Kotlin em `domain/model/` do app Android.

### Enums

```
ProjectStatus : WAITING | IN_PROGRESS | DONE | CANCELLED
TaskStatus    : PENDING | DONE | CANCELLED
Priority      : LOW | MEDIUM | HIGH
```

### Project

```json
{
  "id": 1,
  "name": "App Mobile",
  "status": "IN_PROGRESS",
  "created_at": "2026-05-05T10:00:00Z",
  "completed_at": null,
  "tasks": [ <Task> ]
}
```

Campos computados (não persistidos, calculados na resposta):

| Campo | Tipo | Derivação |
|---|---|---|
| `pending_count` | int | `tasks.count(status == PENDING)` |
| `can_finish` | bool | `tasks não vazio && pending_count == 0` |
| `is_active` | bool | `status == IN_PROGRESS` |

### Task

```json
{
  "id": 1,
  "project_id": 1,
  "title": "Setup do projeto",
  "status": "PENDING",
  "priority": "HIGH",
  "created_at": "2026-05-05T11:00:00Z",
  "completed_at": null
}
```

### TaskWithProject (visão global de tasks)

```json
{
  "task_id": 1,
  "title": "Setup do projeto",
  "status": "PENDING",
  "priority": "HIGH",
  "created_at": "2026-05-05T11:00:00Z",
  "completed_at": null,
  "project_id": 1,
  "project_name": "App Mobile"
}
```

---

## Regras de negócio

Derivadas de `domain/rules/ProjectRules.kt`. Violações retornam **409 Conflict**.

| Operação | Condição para permitir |
|---|---|
| Adicionar task | `project.status == IN_PROGRESS` |
| Completar tasks | `project.status == IN_PROGRESS` |
| Cancelar tasks | `project.status == IN_PROGRESS` |
| Iniciar projeto | `project.status == WAITING` |
| Finalizar projeto | `project.status == IN_PROGRESS && can_finish == true` |
| Cancelar projeto | `project.status != DONE` |
| Excluir projeto | `project.status != IN_PROGRESS` |

---

## Endpoints

### Projetos

#### `GET /projects`

Lista todos os projetos com suas tasks embutidas.

Query params:

| Param | Valores | Default | Descrição |
|---|---|---|---|
| `sort` | `name_asc`, `newest`, `oldest` | `name_asc` | Ordem de exibição |

Response `200`:
```json
[
  {
    "id": 1,
    "name": "App Mobile",
    "status": "IN_PROGRESS",
    "created_at": "2026-05-05T10:00:00Z",
    "completed_at": null,
    "pending_count": 2,
    "can_finish": false,
    "is_active": true,
    "tasks": [...]
  }
]
```

---

#### `POST /projects`

Cria um projeto. Status inicial: `WAITING`.

Request:
```json
{ "name": "Novo Projeto" }
```

Response `201`:
```json
{
  "id": 6,
  "name": "Novo Projeto",
  "status": "WAITING",
  "created_at": "2026-06-04T20:00:00Z",
  "completed_at": null,
  "pending_count": 0,
  "can_finish": false,
  "is_active": false,
  "tasks": []
}
```

---

#### `GET /projects/{project_id}`

Retorna um projeto pelo ID, com tasks embutidas.

Response `200`: mesmo schema do item da lista.  
Response `404`: projeto não encontrado.

---

#### `DELETE /projects/{project_id}`

Exclui um projeto. Regra: `status != IN_PROGRESS`.

Response `204`: sem corpo.  
Response `404`: projeto não encontrado.  
Response `409`: projeto está `IN_PROGRESS` — não pode ser excluído diretamente.

---

### Ciclo de vida do projeto

#### `POST /projects/{project_id}/start`

`WAITING → IN_PROGRESS`

Response `200`: projeto atualizado.  
Response `409`: `status != WAITING`.

---

#### `POST /projects/{project_id}/finish`

`IN_PROGRESS → DONE`. Define `completed_at = now()`.

Response `200`: projeto atualizado.  
Response `409`: `status != IN_PROGRESS` ou `can_finish == false` (ainda há tasks pendentes).

---

#### `POST /projects/{project_id}/cancel`

`* → CANCELLED` (exceto quando já `DONE`).

Response `200`: projeto atualizado.  
Response `409`: `status == DONE`.

---

### Tasks

#### `POST /projects/{project_id}/tasks`

Adiciona uma task ao projeto. Regra: `project.status == IN_PROGRESS`.

Request:
```json
{
  "title": "Criar tela de login",
  "priority": "HIGH"
}
```

Response `201`:
```json
{
  "id": 42,
  "project_id": 1,
  "title": "Criar tela de login",
  "status": "PENDING",
  "priority": "HIGH",
  "created_at": "2026-06-04T20:05:00Z",
  "completed_at": null
}
```

Response `409`: projeto não é `IN_PROGRESS`.

---

#### `PATCH /projects/{project_id}/tasks/complete`

Marca um conjunto de tasks como `DONE`. Define `completed_at = now()` para cada uma.  
Regra: `project.status == IN_PROGRESS`.

Request:
```json
{ "task_ids": [1, 2, 3] }
```

Response `200`: projeto atualizado (com tasks atualizadas embutidas).  
Response `409`: projeto não é `IN_PROGRESS`.

---

#### `PATCH /projects/{project_id}/tasks/cancel`

Marca um conjunto de tasks como `CANCELLED`.  
Regra: `project.status == IN_PROGRESS`.

Request:
```json
{ "task_ids": [4, 5] }
```

Response `200`: projeto atualizado.  
Response `409`: projeto não é `IN_PROGRESS`.

---

#### `PATCH /projects/{project_id}/tasks/complete-all`

Marca todas as tasks `PENDING` do projeto como `DONE`. Define `completed_at = now()`.  
Regra: `project.status == IN_PROGRESS`.

Request: sem corpo.

Response `200`: projeto atualizado.  
Response `409`: projeto não é `IN_PROGRESS`.

---

#### `DELETE /projects/{project_id}/tasks`

Remove um conjunto de tasks permanentemente.  
Regra: `project.status == IN_PROGRESS`.

Request:
```json
{ "task_ids": [6, 7] }
```

Response `200`: projeto atualizado.  
Response `409`: projeto não é `IN_PROGRESS`.

---

### Tasks — visão global

#### `GET /tasks`

Retorna todas as tasks de todos os projetos, com informações do projeto embutidas.  
Usado pelo `TaskListScreen` do app.

Query params:

| Param | Valores | Default |
|---|---|---|
| `status` | `pending`, `done`, `cancelled` | (todos) |
| `priority` | `low`, `medium`, `high` | (todas) |
| `q` | string livre | (sem filtro) |

Response `200`:
```json
[
  {
    "task_id": 1,
    "title": "Setup do projeto",
    "status": "PENDING",
    "priority": "HIGH",
    "created_at": "2026-05-05T11:00:00Z",
    "completed_at": null,
    "project_id": 1,
    "project_name": "App Mobile"
  }
]
```

---

## Erros padrão

```json
{ "detail": "Mensagem descritiva do erro" }
```

| Código | Quando |
|---|---|
| `400` | Request malformado (Pydantic validation) |
| `404` | Recurso não encontrado |
| `409` | Regra de negócio violada |
| `422` | Schema inválido (tipos errados, campos obrigatórios ausentes) |

---

## Estrutura sugerida para o servidor

```
app/
├── main.py                  ← FastAPI app + routers
├── models/
│   ├── project.py           ← Pydantic schemas (request/response)
│   └── task.py
├── routers/
│   ├── projects.py          ← /projects e ciclo de vida
│   └── tasks.py             ← /tasks global
├── services/
│   ├── project_service.py   ← regras de negócio (equivalente a ProjectRules.kt)
│   └── task_service.py
└── repository/
    └── in_memory.py         ← começa in-memory, depois substitui por SQLite/Postgres
```

---

## Próximos passos — camada HTTP no app Android

Quando o servidor estiver pronto, a integração no app Android será:

1. Adicionar dependência Retrofit (ou Ktor client) no `build.gradle`
2. Criar `data/HttpProjectRepository.kt` implementando `domain/repository/ProjectRepository.kt`
3. O `InMemoryProjectRepository` continua existindo para testes e previews
4. Nenhum ViewModel nem Screen precisa mudar — o contrato da interface já existe

O único ponto de troca é onde o repositório é instanciado (atualmente em `MainActivity` via `InMemoryProjectRepository.addTask(...)` e nos ViewModels). Com injeção de dependência, seria trivial trocar a implementação.
