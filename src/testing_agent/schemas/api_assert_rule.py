from __future__ import annotations

# ruff: noqa: F401
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ApiAssertRuleRequest(BaseModel):
    name: str
    enabled: bool = True
    order_no: int = Field(default=0, alias="orderNo")
    assert_source: str = Field(alias="assertSource")
    target_expr: str = Field(default="", alias="targetExpr")
    comparator: str
    expected_value: str = Field(default="", alias="expectedValue")
    model_config = ConfigDict(populate_by_name=True)


class ApiAssertRuleUpdateRequest(BaseModel):
    name: str | None = None
    enabled: bool | None = None
    order_no: int | None = Field(default=None, alias="orderNo")
    assert_source: str | None = Field(default=None, alias="assertSource")
    target_expr: str | None = Field(default=None, alias="targetExpr")
    comparator: str | None = None
    expected_value: str | None = Field(default=None, alias="expectedValue")
    model_config = ConfigDict(populate_by_name=True)


class ApiAssertRuleResponse(ApiAssertRuleRequest):
    assert_rule_id: str = Field(alias="assertRuleId")
    case_id: str = Field(alias="caseId")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
