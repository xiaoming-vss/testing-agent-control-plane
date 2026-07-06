from __future__ import annotations

# ruff: noqa: F401
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FunctionCaseRequest(BaseModel):
    module: str = ""
    title: str
    preconditions: str = ""
    steps: str = ""
    expected_results: str = Field(default="", alias="expectedResults")
    priority: str = ""
    case_type: str = Field(default="", alias="caseType")
    order_no: int = Field(default=0, alias="orderNo")
    model_config = ConfigDict(populate_by_name=True)


class FunctionCaseUpdateRequest(BaseModel):
    module: str | None = None
    title: str | None = None
    preconditions: str | None = None
    steps: str | None = None
    expected_results: str | None = Field(default=None, alias="expectedResults")
    priority: str | None = None
    case_type: str | None = Field(default=None, alias="caseType")
    order_no: int | None = Field(default=None, alias="orderNo")
    model_config = ConfigDict(populate_by_name=True)


class FunctionCaseResponse(FunctionCaseRequest):
    case_id: str = Field(alias="caseId")
    suite_id: str = Field(alias="suiteId")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FunctionCaseImportResponse(BaseModel):
    imported: int


class FunctionCaseZentaoImportResponse(BaseModel):
    suite_id: str = Field(alias="suiteId")
    status: str
    request: Any
    model_config = ConfigDict(populate_by_name=True)
