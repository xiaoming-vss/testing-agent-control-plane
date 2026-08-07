from __future__ import annotations

# ruff: noqa: F401
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


def parse_steps_json(value: Any) -> list[Any]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError("stepsJson 必须是合法的 JSON 数组") from exc
    if not isinstance(value, list):
        raise ValueError("stepsJson 必须是数组")
    return value


class UiCaseRequest(BaseModel):
    name: str
    enabled: bool = True
    order_no: int = Field(default=0, alias="orderNo")
    steps_json: list[Any] = Field(alias="stepsJson")
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("steps_json", mode="before")
    @classmethod
    def validate_steps_json(cls, value: Any) -> list[Any]:
        return parse_steps_json(value)


class UiCaseUpdateRequest(BaseModel):
    name: str | None = None
    enabled: bool | None = None
    order_no: int | None = Field(default=None, alias="orderNo")
    steps_json: list[Any] | None = Field(default=None, alias="stepsJson")
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("steps_json", mode="before")
    @classmethod
    def validate_steps_json(cls, value: Any) -> list[Any] | None:
        return None if value is None else parse_steps_json(value)

class UiCaseResponse(UiCaseRequest):
    case_id: str = Field(alias="caseId")
    suite_id: str = Field(alias="suiteId")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UiCaseImportResponse(BaseModel):
    imported: int
