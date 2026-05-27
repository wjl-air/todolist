from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
import pymysql

app = FastAPI(title="TodoList API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'root'),
    'database': os.environ.get('DB_NAME', '1111'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

class Todo(BaseModel):
    id: Optional[int] = None
    title: str
    completed: bool = False
    created_at: Optional[datetime] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None

@app.get("/api/todos")
def get_todos(db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM todos ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    return rows

@app.post("/api/todos")
def create_todo(todo: Todo, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO todos (title, completed) VALUES (%s, %s)",
        (todo.title, int(todo.completed))
    )
    db.commit()
    tid = cursor.lastrowid
    cursor.execute("SELECT * FROM todos WHERE id = %s", (tid,))
    row = cursor.fetchone()
    cursor.close()
    return row

@app.put("/api/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate, db=Depends(get_db)):
    cursor = db.cursor()
    sets = []
    params = []
    if todo.title is not None:
        sets.append("title = %s")
        params.append(todo.title)
    if todo.completed is not None:
        sets.append("completed = %s")
        params.append(int(todo.completed))
    if not sets:
        cursor.close()
        return {"detail": "No fields to update"}
    params.append(todo_id)
    cursor.execute(f"UPDATE todos SET {', '.join(sets)} WHERE id = %s", params)
    db.commit()
    cursor.execute("SELECT * FROM todos WHERE id = %s", (todo_id,))
    row = cursor.fetchone()
    cursor.close()
    return row

@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    db.commit()
    cursor.close()
    return {"ok": True}
