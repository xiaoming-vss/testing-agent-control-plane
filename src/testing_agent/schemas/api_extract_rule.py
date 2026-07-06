from __future__ import annotations

# ruff: noqa: F401
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ApiExtractRuleRequest(BaseModel):
    name: str
    enabled: bool = True
    order_no: int = Field(default=0, alias="orderNo")
    source: str
    source_expr: str = Field(default="", alias="sourceExpr")
    var_key: str = Field(alias="varKey")
    default_value: str = Field(default="", alias="defaultValue")
    model_config = ConfigDict(populate_by_name=True)


class ApiExtractRuleUpdateRequest(BaseModel):
    name: str | None = None
    enabled: bool | None = None
    order_no: int | None = Field(default=None, alias="orderNo")
    source: str | None = None
    source_expr: str | None = Field(default=None, alias="sourceExpr")
    var_key: str | None = Field(default=None, alias="varKey")
    default_value: str | None = Field(default=None, alias="defaultValue")
    model_config = ConfigDict(populate_by_name=True)


class ApiExtractRuleResponse(ApiExtractRuleRequest):
    extract_rule_id: str = Field(alias="extractRuleId")
    case_id: str = Field(alias="caseId")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
