from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class BookingBase(BaseModel):
    customer_id: Optional[int] = None
    service_id: int
    starts_at: datetime
    ends_at: datetime
    notes: Optional[str] = None


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(requested|confirmed|completed|cancelled)$")


class BookingStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(requested|confirmed|completed|cancelled)$")


class BookingResponse(BookingBase):
    id: int
    workspace_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)