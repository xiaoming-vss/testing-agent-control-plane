from __future__ import annotations

# ruff: noqa: F401
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ApiEnvironmentVarRequest(BaseModel):
    var_key: str = Field(alias="varKey")
    value: str = ""
    description: str = ""
    is_secret: bool = Field(default=False, alias="isSecret")
    model_config = ConfigDict(populate_by_name=True)


class ApiEnvironmentVarUpdateRequest(BaseModel):
    var_key: str | None = Field(default=None, alias="varKey")
    value: str | None = None
    description: str | None = None
    is_secret: bool | None = Field(default=None, alias="isSecret")
    model_config = ConfigDict(populate_by_name=True)


class ApiEnvironmentVarResponse(ApiEnvironmentVarRequest):
    env_var_id: str = Field(alias="envVarId")
    environment_id: str = Field(alias="environmentId")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
