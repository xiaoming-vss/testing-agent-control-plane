from __future__ import annotations

# ruff: noqa: F401
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UiCaseRequest(BaseModel):
    name: str
    enabled: bool = True
    order_no: int = Field(default=0, alias="orderNo")
    steps_json: Any = Field(alias="stepsJson")
    model_config = ConfigDict(populate_by_name=True)


class UiCaseUpdateRequest(BaseModel):
    name: str | None = None
    enabled: bool | None = None
    order_no: int | None = Field(default=None, alias="orderNo")
    steps_json: Any | None = Field(default=None, alias="stepsJson")
    model_config = ConfigDict(populate_by_name=True)

class UiCaseResponse(UiCaseRequest):
    case_id: str = Field(alias="caseId")
    suite_id: str = Field(alias="suiteId")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UiCaseImportResponse(BaseModel):
    imported: int
