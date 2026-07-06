from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateSprintRequest(BaseModel):
    name: str
    description: str = ""
    start_time: str = Field(alias="startTime")
    end_time: str | None = Field(default=None, alias="endTime")

    model_config = ConfigDict(populate_by_name=True)

class UpdateSprintRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    start_time: str | None = Field(default=None, alias="startTime")
    end_time: str | None = Field(default=None, alias="endTime")

    model_config = ConfigDict(populate_by_name=True)

class SprintResponse(BaseModel):
    sprint_id: str = Field(alias="sprintId")
    project_id: str = Field(alias="projectId")
    name: str
    description: str = ""
    status: str
    start_time: datetime | str | None = Field(default="", alias="startTime")
    end_time: datetime | str | None = Field(default="", alias="endTime")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
