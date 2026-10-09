from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class CustomerBase(BaseModel):
    display_name: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    address: Optional[str] = None
    consent_status: str = Field(default="unknown", pattern="^(opted_in|opted_out|unknown)$")
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    display_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    consent_status: Optional[str] = Field(None, pattern="^(opted_in|opted_out|unknown)$")
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: int
    workspace_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)