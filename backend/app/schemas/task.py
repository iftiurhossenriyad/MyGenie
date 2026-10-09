from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    priority: str = Field(default="normal", pattern="^(low|normal|high)$")
    workspace_id: Optional[int] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(pending|completed|archived)$")
    priority: Optional[str] = Field(None, pattern="^(low|normal|high)$")


class TaskResponse(TaskBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)