from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime


class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    type: str = Field(default="business", pattern="^(personal|business)$")

    @field_validator("name", mode="before")
    @classmethod
    def strip_workspace_name(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceResponse(WorkspaceBase):
    id: int
    owner_user_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceMemberBase(BaseModel):
    user_id: int
    role: str = Field(default="staff", pattern="^(owner|staff|member|customer)$")


class WorkspaceMemberCreate(WorkspaceMemberBase):
    pass


class WorkspaceMemberResponse(WorkspaceMemberBase):
    id: int
    workspace_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)