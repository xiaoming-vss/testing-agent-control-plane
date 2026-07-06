from __future__ import annotations

# ruff: noqa: F401
import json
from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_serializer


def json_text(value: Any, default: str = "{}") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value or default
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class RunApiCaseRequest(BaseModel):
    environment_id: str = Field(alias="environmentId")
    model_config = ConfigDict(populate_by_name=True)

class RunApiCollectionRequest(RunApiCaseRequest):
    pass

class ApiCaseRunResponse(BaseModel):
    run_id: str = Field(alias="runId")
    case_id: str = Field(alias="caseId")
    collection_id: str = Field(alias="collectionId")
    collection_run_id: str | None = Field(default=None, alias="collectionRunId")
    environment_id: str = Field(alias="environmentId")
    status: str
    success: bool = False
    error_message: str = Field(alias="errorMessage")
    duration_ms: int = Field(alias="durationMs")
    request: Any | None = Field(
        default=None,
        validation_alias=AliasChoices("request", "request_snapshot_json"),
        serialization_alias="request",
    )
    response: Any | None = Field(
        default=None,
        validation_alias=AliasChoices("response", "response_snapshot_json"),
        serialization_alias="response",
    )
    runtime_vars_json: Any | None = Field(
        default=None,
        validation_alias=AliasChoices("runtimeVarsJson", "runtime_vars_json"),
        serialization_alias="runtimeVarsJson",
    )
    extract_results: list[Any] | None = Field(
        default=None,
        validation_alias=AliasChoices("extractResults", "extract_results_json"),
        serialization_alias="extractResults",
    )
    assert_results: list[Any] | None = Field(
        default=None,
        validation_alias=AliasChoices("assertResults", "assert_results_json"),
        serialization_alias="assertResults",
    )
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_serializer("runtime_vars_json")
    def serialize_runtime_vars_json(self, value: Any) -> str:
        return json_text(value)

class ApiCollectionRunResponse(BaseModel):
    collection_run_id: str = Field(alias="collectionRunId")
    collection_id: str = Field(alias="collectionId")
    requirement_id: str = Field(alias="requirementId")
    sprint_id: str = Field(alias="sprintId")
    project_id: str = Field(alias="projectId")
    environment_id: str = Field(alias="environmentId")
    trigger_user_id: str = Field(alias="triggerUserId")
    trigger_type: str = Field(alias="triggerType")
    status: str
    total_count: int = Field(alias="totalCount")
    success_count: int = Field(alias="successCount")
    failed_count: int = Field(alias="failedCount")
    error_count: int = Field(alias="errorCount")
    skipped_count: int = Field(alias="skippedCount")
    runtime_vars_json: Any | None = Field(
        default=None,
        validation_alias=AliasChoices("runtimeVarsJson", "runtime_vars_json"),
        serialization_alias="runtimeVarsJson",
    )
    error_message: str = Field(alias="errorMessage")
    started_at: datetime | str | None = Field(default="", alias="startedAt")
    finished_at: datetime | str | None = Field(default="", alias="finishedAt")
    duration_ms: int = Field(alias="durationMs")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_serializer("runtime_vars_json")
    def serialize_runtime_vars_json(self, value: Any) -> str:
        return json_text(value)


class ApiCollectionRunReportItem(BaseModel):
    item_id: str = Field(alias="itemId")
    case_id: str = Field(alias="caseId")
    case_run_id: str = Field(alias="caseRunId")
    case_name: str = Field(alias="caseName")
    order_no: int = Field(alias="orderNo")
    status: str
    continue_on_failure: bool = Field(alias="continueOnFailure")
    error_message: str = Field(alias="errorMessage")
    started_at: str = Field(alias="startedAt")
    finished_at: str = Field(alias="finishedAt")
    duration_ms: int = Field(alias="durationMs")
    request: Any
    response: Any
    runtime_vars_json: str = Field(alias="runtimeVarsJson")
    extract_results: list[Any] = Field(alias="extractResults")
    assert_results: list[Any] = Field(alias="assertResults")

    model_config = ConfigDict(populate_by_name=True)


class ApiCollectionRunReportResponse(ApiCollectionRunResponse):
    items: list[ApiCollectionRunReportItem]
