"""
FastAPI Task Manager

This is the ENTIRE backend — routing, validation, and logic — in one file.
Compare this to Django where the same functionality is split across
models.py, serializers.py, views.py, and urls.py.

Run with:  uvicorn main:app --reload
"""

from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3

app = FastAPI()


# === THE DATABASE ===
# A SQLite file (tasks.db), queried with plain SQL through Python's built-in
# sqlite3 module. Django does the same with an ORM that writes the SQL for you.

DB_PATH = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            description TEXT    NOT NULL DEFAULT '',
            completed   INTEGER NOT NULL DEFAULT 0,
            created_at  TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()


def get_db():
    # check_same_thread=False: FastAPI may open the connection and run the
    # route in different threads. Safe here: one connection per request.
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row   # rows behave like dicts: row["title"]
    try:
        yield conn
    finally:
        conn.close()

def fetch_task(db, task_id):
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(row)


# === THE "SERIALIZER" ===
# In Django, the serializer is a separate file. In FastAPI, it's a Pydantic model.
# Same job: defines what fields exist and validates incoming data.

class TaskIn(BaseModel):
    """What the frontend sends when creating a task."""
    title: str
    description: str = ""
    completed: bool = False


class TaskUpdate(BaseModel):
    """What the frontend sends for a PATCH: every field is optional."""
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TaskOut(BaseModel):
    """What the API sends back to the frontend."""
    id: int
    title: str
    description: str
    completed: bool
    created_at: str


# === THE ROUTES ===
# In Django, these are split across urls.py (routing) and views.py (logic).
# In FastAPI, each route is one function with a decorator that says
# the URL and the HTTP method. Nothing is hidden.
# response_model=TaskOut also turns the stored 0/1 back into false/true.


# GET /api/tasks/ — list all tasks
@app.get("/api/tasks/", response_model=list[TaskOut])
def list_tasks(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    return [dict(row) for row in rows]


# POST /api/tasks/ — create a new task
@app.post("/api/tasks/", status_code=201, response_model=TaskOut)
def create_task(task: TaskIn, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute(
        "INSERT INTO tasks (title, description, completed, created_at) VALUES (?, ?, ?, ?)",
        (task.title, task.description, task.completed, datetime.now().isoformat()),
    )
    db.commit()
    return fetch_task(db, cursor.lastrowid)


# GET /api/tasks/{id}/ — get one task
@app.get("/api/tasks/{task_id}/", response_model=TaskOut)
def get_task(task_id: int, db: sqlite3.Connection = Depends(get_db)):
    return fetch_task(db, task_id)


# PATCH /api/tasks/{id}/ — partially update a task
@app.patch("/api/tasks/{task_id}/", response_model=TaskOut)
def update_task(task_id: int, updates: TaskUpdate, db: sqlite3.Connection = Depends(get_db)):
    fetch_task(db, task_id)   # 404 if it doesn't exist
    # exclude_unset: only the fields the client actually sent
    fields = updates.model_dump(exclude_unset=True, exclude_none=True)
    if fields:
        # Column names come from TaskUpdate's fields, so the f-string is safe.
        # Values always go through ? placeholders.
        set_clause = ", ".join(f"{column} = ?" for column in fields)
        db.execute(
            f"UPDATE tasks SET {set_clause} WHERE id = ?",
            (*fields.values(), task_id),
        )
        db.commit()
    return fetch_task(db, task_id)


# DELETE /api/tasks/{id}/ — delete a task
@app.delete("/api/tasks/{task_id}/", status_code=204)
def delete_task(task_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")


# GET / — serve the frontend HTML page
@app.get("/", response_class=HTMLResponse)
def frontend():
    with open("index.html") as f:
        return f.read()
