from __future__ import annotations

# ruff: noqa: F401
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ApiEnvironmentRequest(BaseModel):
    name: str
    base_url: str = Field(default="", alias="baseUrl")
    description: str = ""
    is_default: bool = Field(default=False, alias="isDefault")
    model_config = ConfigDict(populate_by_name=True)


class ApiEnvironmentUpdateRequest(BaseModel):
    name: str | None = None
    base_url: str | None = Field(default=None, alias="baseUrl")
    description: str | None = None
    is_default: bool | None = Field(default=None, alias="isDefault")
    model_config = ConfigDict(populate_by_name=True)


class ApiEnvironmentResponse(ApiEnvironmentRequest):
    environment_id: str = Field(alias="environmentId")
    project_id: str = Field(alias="projectId")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
