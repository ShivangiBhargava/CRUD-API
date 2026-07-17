# CRUD-API
Building a small API that manages a to-do list — create, read, update and delete tasks — test it in Swagger UI, and publish it to GitHub.

# Task API

A RESTful CRUD API for managing a to-do list, built with [FastAPI](https://fastapi.tiangolo.com/) (Python).  

---

## How to run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
uvicorn main:app --reload
```

The API is now live at **http://localhost:8000**  
Interactive Swagger docs: **http://localhost:8000/docs**

---

## Endpoints

| Method | Path | Description | Success code |
|--------|------|-------------|--------------|
| `GET` | `/` | API info | 200 |
| `GET` | `/health` | Health check | 200 |
| `GET` | `/tasks` | List all tasks | 200 |
| `GET` | `/tasks/{id}` | Get one task | 200 |
| `POST` | `/tasks` | Create a task | 201 |
| `PUT` | `/tasks/{id}` | Update a task | 200 |
| `DELETE` | `/tasks/{id}` | Delete a task | 204 |
| `GET` | `/stats` | Task statistics | 200 |
| `POST` | `/reset` | Reset to defaults | 200 |

---

## Status codes used

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Successful read or update |
| 201 | Created | Task successfully created |
| 204 | No Content | Task successfully deleted |
| 400 | Bad Request | Missing/empty `title`, or empty update body |
| 404 | Not Found | No task with the given ID |

---

## curl examples

### Create a task (→ 201)
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'
```

```
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

### List all tasks (→ 200)
```bash
curl -i http://localhost:8000/tasks
```

### Get one task (→ 200 or 404)
```bash
curl -i http://localhost:8000/tasks/1
curl -i http://localhost:8000/tasks/99   # → 404
```

### Update a task (→ 200)
```bash
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done":true}'
```

### Delete a task (→ 204)
```bash
curl -i -X DELETE http://localhost:8000/tasks/1
```

### Validation error (→ 400)
```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## Data model

Each task is a JSON object:
```json
{ "id": 1, "title": "Buy groceries", "done": false }
```

Data is stored **in memory only** — it resets when the server restarts. This is intentional for Week 2; a persistent database (PostgreSQL + SQLAlchemy) is added in Week 3.

> **The mortality experiment (★ stretch):** After restarting the server, all tasks created during the previous session disappear. This happens because Python variables live in the process's RAM — the moment the process exits, that memory is freed. A database writes to disk, so data survives restarts. That's the entire reason Week 3 exists.

---

## Extras implemented

- **`GET /stats`** — returns `{ total, done, open }` counts
- **`POST /reset`** — restores the three seed tasks (handy for demos)

---

## Commit history

```
Stage 0: hello server
Stage 1: root and health endpoints
Stage 2: read endpoints with 404
Stage 3: create with validation
Stage 4: full CRUD
Stage 5: Swagger UI (FastAPI built-in at /docs)
Stage 6: publish and docs
```

---

## AI vs me (Stage 7)

### My prompt

> Build a CRUD REST API in Python using FastAPI that manages a to-do list stored in memory (no database). The API must have these five endpoints:
> - GET /tasks — return all tasks as a JSON array
> - GET /tasks/{id} — return one task; 404 with JSON error if not found
> - POST /tasks — create a task from `{"title": "..."}` body; assign auto-incrementing id; set done=false; return the task with 201; return 400 with a JSON error if title is missing or empty
> - PUT /tasks/{id} — update title and/or done; 404 for unknown id; 400 if the body is empty or invalid
> - DELETE /tasks/{id} — remove the task; return 204 with no body; 404 for unknown id
>
> Also add GET / returning `{"name":"Task API","version":"1.0","endpoints":["/tasks"]}` and GET /health returning `{"status":"ok"}`.
> Pre-populate three example tasks. Use Pydantic for input validation. Serve Swagger UI at /docs (it's free in FastAPI). Include a requirements.txt.

### Three concrete differences found

1. **The AI returned 422 for missing fields instead of 400.** FastAPI's default Pydantic validation raises a 422 Unprocessable Entity — the AI left that default in place. My version overrides validation errors to return 400 with a plain JSON `{ "detail": "..." }` message as the assignment requires.
2. **The AI used a mutable default argument for the task list** — a classic Python bug where the list is shared across calls. My version declares `tasks` at module scope correctly.
3. **The AI didn't validate an empty PUT body** — sending `{}` returned 200 and silently changed nothing. My version checks that at least one field is provided and returns 400 otherwise.

### What my prompt forgot

The prompt didn't say what the 400 error *body* should look like. The AI returned FastAPI's verbose Pydantic error structure (a nested `detail` array) instead of a simple `{"detail": "title must not be empty"}`. Next time I'd add: *"All error responses must be plain JSON objects with a single string `detail` key."*

### One-sentence rematch result

After adding that constraint, the AI's second attempt matched my version almost exactly — confirming that precision in the spec is the real skill, not prompting.
