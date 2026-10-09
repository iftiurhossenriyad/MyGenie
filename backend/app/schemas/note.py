from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    body: Optional[str] = None
    workspace_id: Optional[int] = None


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    body: Optional[str] = None


class NoteResponse(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)