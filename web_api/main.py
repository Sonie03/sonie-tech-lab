from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
import sqlite3
import os
from datetime import datetime

app = FastAPI(title="DevBuddy AI Web API")

# Instrument the FastAPI app to expose /metrics
Instrumentator().instrument(app).expose(app)

# Use a local database for the web container
DB_PATH = os.path.join(os.path.dirname(__file__), "web_devbuddy.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            priority TEXT,
            due_date TEXT,
            category TEXT,
            completed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class TaskCreate(BaseModel):
    title: str
    priority: str = "Medium"
    due_date: str
    category: str = "General"

@app.get("/")
def read_root():
    return {"message": "Welcome to DevBuddy AI Web API!"}

@app.get("/tasks")
def get_tasks():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, priority, due_date, category, completed FROM tasks")
    rows = c.fetchall()
    conn.close()
    
    tasks = []
    for r in rows:
        tasks.append({
            "id": r[0],
            "title": r[1],
            "priority": r[2],
            "due_date": r[3],
            "category": r[4],
            "completed": bool(r[5])
        })
    return {"tasks": tasks}

@app.post("/tasks")
def create_task(task: TaskCreate):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks (title, priority, due_date, category) VALUES (?, ?, ?, ?)",
        (task.title, task.priority, task.due_date, task.category)
    )
    conn.commit()
    task_id = c.lastrowid
    conn.close()
    return {"message": "Task created successfully", "task_id": task_id}

@app.put("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.commit()
    conn.close()
    return {"message": "Task marked as completed"}
