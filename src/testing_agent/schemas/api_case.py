from __future__ import annotations

# ruff: noqa: F401
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ApiCaseRequest(BaseModel):
    name: str
    description: str = ""
    enabled: bool = True
    order_no: int = Field(default=0, alias="orderNo")
    method: str
    url_template: str = Field(alias="urlTemplate")
    headers_json: str = Field(default="", alias="headersJson")
    query_json: str = Field(default="", alias="queryJson")
    body_type: str = Field(default="json", alias="bodyType")
    body_json: str = Field(default="", alias="bodyJson")
    body_text: str = Field(default="", alias="bodyText")
    timeout_ms: int = Field(default=5000, alias="timeoutMs")
    continue_on_failure: bool = Field(default=False, alias="continueOnFailure")
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("headers_json", "query_json", "body_json", mode="before")
    @classmethod
    def dump_json_like_value(cls, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)


class ApiCaseUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    enabled: bool | None = None
    order_no: int | None = Field(default=None, alias="orderNo")
    method: str | None = None
    url_template: str | None = Field(default=None, alias="urlTemplate")
    headers_json: str | None = Field(default=None, alias="headersJson")
    query_json: str | None = Field(default=None, alias="queryJson")
    body_type: str | None = Field(default=None, alias="bodyType")
    body_json: str | None = Field(default=None, alias="bodyJson")
    body_text: str | None = Field(default=None, alias="bodyText")
    timeout_ms: int | None = Field(default=None, alias="timeoutMs")
    continue_on_failure: bool | None = Field(default=None, alias="continueOnFailure")
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("headers_json", "query_json", "body_json", mode="before")
    @classmethod
    def dump_json_like_value(cls, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)

class ApiCaseResponse(ApiCaseRequest):
    case_id: str = Field(alias="caseId")
    collection_id: str = Field(alias="collectionId")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
