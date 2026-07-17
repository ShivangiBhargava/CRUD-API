"""
Task API Assignment 
A CRUD API for managing a to-do list, built with FastAPI.
Swagger UI available at http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from typing import Optional

# ── App setup ──────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Task API",
    description="A CRUD API for managing a to-do list.",
    version="1.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert FastAPI's default 422 validation errors to 400 Bad Request."""
    errors = exc.errors()
    messages = [f"{e['loc'][-1]}: {e['msg']}" for e in errors]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "; ".join(messages)},
    )


# ── In-memory "database" ───────────────────────────────────────────────────────

tasks: list[dict] = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read FastAPI docs", "done": True},
    {"id": 3, "title": "Push code to GitHub", "done": False},
]

next_id: int = 4  # auto-incrementing ID counter


def find_task(task_id: int) -> dict:
    """Return a task by id, or raise 404 if not found."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found",
    )


# ── Request / Response models ──────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v.strip()

    model_config = {"json_schema_extra": {"example": {"title": "Buy milk"}}}


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("title must not be empty")
        return v.strip() if v else v

    model_config = {
        "json_schema_extra": {"example": {"title": "Buy oat milk", "done": True}}
    }


# ── Stage 0 & 1 — Root + Health ────────────────────────────────────────────────

@app.get(
    "/",
    summary="API info",
    description="Returns a short description of the API and its available endpoints.",
    tags=["Meta"],
)
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get(
    "/health",
    summary="Health check",
    description="Used by infrastructure tools to verify the server is alive and responding.",
    tags=["Meta"],
)
def health():
    return {"status": "ok"}


# ── Stage 2 — Read ─────────────────────────────────────────────────────────────

@app.get(
    "/tasks",
    summary="List all tasks",
    description="Returns every task in the in-memory list.",
    tags=["Tasks"],
)
def list_tasks():
    return tasks


@app.get(
    "/tasks/{task_id}",
    summary="Get a single task",
    description="Returns the task with the given ID. Returns 404 if it does not exist.",
    tags=["Tasks"],
)
def get_task(task_id: int):
    return find_task(task_id)


# ── Stage 3 — Create ───────────────────────────────────────────────────────────

@app.post(
    "/tasks",
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
    description="Creates a new task. `title` is required and must not be empty. Returns the created task with its assigned ID.",
    tags=["Tasks"],
)
def create_task(body: TaskCreate):
    global next_id
    task = {"id": next_id, "title": body.title, "done": False}
    tasks.append(task)
    next_id += 1
    return task


# ── Stage 4 — Update & Delete ──────────────────────────────────────────────────

@app.put(
    "/tasks/{task_id}",
    summary="Update a task",
    description="Updates the `title` and/or `done` status of a task. Returns 404 for an unknown ID, 400 if the body is empty.",
    tags=["Tasks"],
)
def update_task(task_id: int, body: TaskUpdate):
    if body.title is None and body.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must include at least one of: title, done",
        )
    task = find_task(task_id)
    if body.title is not None:
        task["title"] = body.title
    if body.done is not None:
        task["done"] = body.done
    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Removes the task with the given ID. Returns 204 (no body) on success, 404 if it does not exist.",
    tags=["Tasks"],
)
def delete_task(task_id: int):
    task = find_task(task_id)
    tasks.remove(task)


# ── Stretch: Stats & Reset ─────────────────────────────────────────────────────

@app.get(
    "/stats",
    summary="Task statistics",
    description="Returns counts of total, done, and open tasks.",
    tags=["Extras"],
)
def stats():
    done = sum(1 for t in tasks if t["done"])
    return {"total": len(tasks), "done": done, "open": len(tasks) - done}


@app.post(
    "/reset",
    summary="Reset tasks",
    description="Restores the three example tasks and resets the ID counter. Useful for demos.",
    tags=["Extras"],
)
def reset():
    global tasks, next_id
    tasks = [
        {"id": 1, "title": "Buy groceries", "done": False},
        {"id": 2, "title": "Read FastAPI docs", "done": True},
        {"id": 3, "title": "Push code to GitHub", "done": False},
    ]
    next_id = 4
    return {"message": "Tasks reset to defaults", "tasks": tasks}
