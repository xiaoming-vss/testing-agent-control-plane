from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateProjectRequest(BaseModel):
    name: str
    description: str = ""

class UpdateProjectRequest(BaseModel):
    name: str | None = None
    description: str | None = None

class ProjectResponse(BaseModel):
    project_id: str = Field(alias="projectId")
    user_id: str = Field(alias="userId")
    name: str
    description: str = ""
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
