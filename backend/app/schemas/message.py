from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class MessageBase(BaseModel):
    content: str = Field(..., min_length=1)
    content_type: str = Field(default="text", pattern="^(text|image|file)$")


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    sender_type: str
    sender_id: Optional[int] = None
    provider_message_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    content: str = Field(..., min_length=1)
    language: str = Field(default="auto", pattern="^(bn|en|auto)$")


class ChatResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
    conversation_id: int