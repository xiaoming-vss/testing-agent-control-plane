from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class DebugRunUiCaseRequest(BaseModel):
    headless: bool | None = None
    slow_mo_ms: int | None = Field(default=None, alias="slowMoMs")
    viewport_width: int | None = Field(default=None, alias="viewportWidth")
    viewport_height: int | None = Field(default=None, alias="viewportHeight")
    default_step_timeout_ms: int | None = Field(default=None, alias="defaultStepTimeoutMs")
    model_config = ConfigDict(populate_by_name=True)

class RunUiSuiteRequest(DebugRunUiCaseRequest):
    pass

class UiCaseRunResponse(BaseModel):
    run_id: str = Field(alias="runId")
    case_id: str = Field(alias="caseId")
    suite_id: str = Field(alias="suiteId")
    requirement_id: str = Field(alias="requirementId")
    sprint_id: str = Field(alias="sprintId")
    project_id: str = Field(alias="projectId")
    trigger_user_id: str = Field(alias="triggerUserId")
    trigger_type: str = Field(alias="triggerType")
    status: str
    success: bool = False
    snapshot: Any | None = Field(
        default=None,
        validation_alias=AliasChoices("snapshot", "snapshot_json"),
        serialization_alias="snapshot",
    )
    step_results: list[Any] | None = Field(
        default=None,
        validation_alias=AliasChoices("stepResults", "step_results_json"),
        serialization_alias="stepResults",
    )
    current_url: str = Field(alias="currentUrl")
    trace_path: str = Field(alias="tracePath")
    error_message: str = Field(alias="errorMessage")
    duration_ms: int = Field(alias="durationMs")
    started_at: datetime | str | None = Field(default="", alias="startedAt")
    finished_at: datetime | str | None = Field(default="", alias="finishedAt")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class UiSuiteRunResponse(BaseModel):
    suite_run_id: str = Field(alias="suiteRunId")
    suite_id: str = Field(alias="suiteId")
    requirement_id: str = Field(alias="requirementId")
    sprint_id: str = Field(alias="sprintId")
    project_id: str = Field(alias="projectId")
    trigger_user_id: str = Field(alias="triggerUserId")
    trigger_type: str = Field(alias="triggerType")
    status: str
    total_count: int = Field(alias="totalCount")
    success_count: int = Field(alias="successCount")
    failed_count: int = Field(alias="failedCount")
    error_count: int = Field(alias="errorCount")
    skipped_count: int = Field(alias="skippedCount")
    current_url: str = Field(alias="currentUrl")
    trace_path: str = Field(alias="tracePath")
    error_message: str = Field(alias="errorMessage")
    started_at: datetime | str | None = Field(default="", alias="startedAt")
    finished_at: datetime | str | None = Field(default="", alias="finishedAt")
    duration_ms: int = Field(alias="durationMs")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UiSuiteRunReportItem(BaseModel):
    item_id: str = Field(alias="itemId")
    case_id: str = Field(alias="caseId")
    status: str
    order_no: int = Field(alias="orderNo")

    model_config = ConfigDict(populate_by_name=True)


class UiSuiteRunReportResponse(UiSuiteRunResponse):
    items: list[UiSuiteRunReportItem]
