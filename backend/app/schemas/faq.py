from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class FAQBase(BaseModel):
    question: str = Field(..., min_length=2)
    answer: str = Field(..., min_length=1)
    question_bn: Optional[str] = None
    answer_bn: Optional[str] = None
    question_en: Optional[str] = None
    answer_en: Optional[str] = None
    language: str = Field(default="bn", pattern="^(bn|en)$")


class FAQCreate(FAQBase):
    pass


class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    question_bn: Optional[str] = None
    answer_bn: Optional[str] = None
    question_en: Optional[str] = None
    answer_en: Optional[str] = None
    language: Optional[str] = Field(None, pattern="^(bn|en)$")
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$")


class FAQResponse(FAQBase):
    id: int
    workspace_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)