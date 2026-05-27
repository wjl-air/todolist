from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TodoCreate(BaseModel):
    title: str
    completed: bool = False

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None

class TodoResponse(BaseModel):
    id: int
    title: str
    completed: bool
    created_at: Optional[datetime] = None
