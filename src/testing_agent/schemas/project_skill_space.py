from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectSkillSpaceResponse(BaseModel):
    skill_space_id: str = Field(alias="skillSpaceId")
    project_id: str = Field(alias="projectId")
    version: int = 0
    hash: str = ""
    download_url: str = Field(default="", alias="downloadUrl")
    filename: str = ""
    size: int = 0
    is_default: bool = Field(default=False, alias="isDefault")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")

    model_config = ConfigDict(populate_by_name=True)


class ProjectSkillSyncResponse(BaseModel):
    project_id: str = Field(alias="projectId")
    status: str

    model_config = ConfigDict(populate_by_name=True)
