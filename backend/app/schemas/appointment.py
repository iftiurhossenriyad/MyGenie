from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class AppointmentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    notes: Optional[str] = None
    starts_at: datetime
    ends_at: Optional[datetime] = None
    workspace_id: Optional[int] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    notes: Optional[str] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(scheduled|cancelled|completed)$")


class AppointmentResponse(AppointmentBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)