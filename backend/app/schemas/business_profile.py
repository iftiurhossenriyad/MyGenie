from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class BusinessProfileBase(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[str] = None
    delivery_info: Optional[str] = None
    policies: Optional[str] = None
    default_language: str = Field(default="bn", pattern="^(bn|en)$")
    supported_languages: str = Field(default="bn,en")


class BusinessProfileCreate(BusinessProfileBase):
    pass


class BusinessProfileUpdate(BaseModel):
    business_name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[str] = None
    delivery_info: Optional[str] = None
    policies: Optional[str] = None
    default_language: Optional[str] = Field(None, pattern="^(bn|en)$")
    supported_languages: Optional[str] = None


class BusinessProfileResponse(BusinessProfileBase):
    id: int
    workspace_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)