from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ConversationBase(BaseModel):
    channel: str = Field(default="web", pattern="^(web|whatsapp|messenger|email|sms)$")
    language: str = Field(default="bn", pattern="^(bn|en|auto)$")


class ConversationCreate(ConversationBase):
    workspace_id: int
    customer_id: Optional[int] = None


class ConversationUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(active|handoff|closed)$")
    assigned_staff_id: Optional[int] = None
    language: Optional[str] = Field(None, pattern="^(bn|en|auto)$")


class ConversationResponse(ConversationBase):
    id: int
    workspace_id: int
    owner_user_id: Optional[int] = None
    customer_id: Optional[int] = None
    status: str
    assigned_staff_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class HandoffRequest(BaseModel):
    reason: Optional[str] = None