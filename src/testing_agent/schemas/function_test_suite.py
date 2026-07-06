from __future__ import annotations

# ruff: noqa: F401
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FunctionSuiteRequest(BaseModel):
    name: str
    description: str = ""


class FunctionSuiteUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None


class FunctionSuiteResponse(BaseModel):
    suite_id: str = Field(alias="suiteId")
    requirement_id: str = Field(alias="requirementId")
    name: str
    description: str = ""
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
