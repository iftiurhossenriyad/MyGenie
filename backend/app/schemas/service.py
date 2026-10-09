from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal


class ServiceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    duration_minutes: int = Field(default=30, gt=0)
    capacity: int = Field(default=1, gt=0)
    price: Optional[Decimal] = Field(None, ge=0)
    currency: str = Field(default="BDT", max_length=10)


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    capacity: Optional[int] = Field(None, gt=0)
    price: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(active|inactive|archived)$")


class ServiceResponse(ServiceBase):
    id: int
    workspace_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)