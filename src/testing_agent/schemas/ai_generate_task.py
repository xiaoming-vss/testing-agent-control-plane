from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AiGenerateTaskRequest(BaseModel):
    name: str | None = None
    sprint_id: str | None = Field(default=None, alias="sprintId")
    requirement_id: str | None = Field(default=None, alias="requirementId")
    source_type: str | None = Field(default=None, alias="sourceType")
    source_content: str | None = Field(default=None, alias="sourceContent")
    instruction: str | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        json_schema_extra={"additionalProperties": False},
    )


class AiGenerateTaskRunRequest(BaseModel):
    connection_id: str | None = Field(default=None, alias="connectionId")
    llm_connection_id: str | None = Field(default=None, alias="llmConnectionId")
    trigger_type: str | None = Field(default=None, alias="triggerType")
    checkpoint_enabled: bool | None = Field(default=None, alias="checkpointEnabled")
    config_json: Any | None = Field(default=None, alias="configJson")
    result_yaml: str | None = Field(default=None, alias="resultYaml")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        json_schema_extra={"additionalProperties": False},
    )


class RequirementAnalysisRunRequest(BaseModel):
    connection_id: str | None = Field(default=None, alias="connectionId")
    llm_connection_id: str | None = Field(default=None, alias="llmConnectionId")
    instruction: str | None = None
    trigger_type: str | None = Field(default=None, alias="triggerType")
    checkpoint_enabled: bool | None = Field(default=None, alias="checkpointEnabled")
    config_json: Any | None = Field(default=None, alias="configJson")
    result_yaml: str | None = Field(default=None, alias="resultYaml")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        json_schema_extra={"additionalProperties": False},
    )


class RequirementAnalysisTaskRequest(BaseModel):
    name: str | None = None
    requirement_id: str | None = Field(default=None, alias="requirementId")
    instruction: str | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        json_schema_extra={"additionalProperties": False},
    )


class TestReportGenerateTaskRequest(BaseModel):
    name: str | None = None
    sprint_id: str | None = Field(default=None, alias="sprintId")
    instruction: str | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        json_schema_extra={"additionalProperties": False},
    )


class TestReportGenerateTaskRunRequest(BaseModel):
    sprint_id: str | None = Field(default=None, alias="sprintId")
    connection_id: str | None = Field(default=None, alias="connectionId")
    llm_connection_id: str | None = Field(default=None, alias="llmConnectionId")
    trigger_type: str | None = Field(default=None, alias="triggerType")
    snapshot_date: str | None = Field(default=None, alias="snapshotDate")
    instruction: str | None = None
    config_json: Any | None = Field(default=None, alias="configJson")
    result_yaml: str | None = Field(default=None, alias="resultYaml")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        json_schema_extra={"additionalProperties": False},
    )


class AiGenerateTaskReviewRequest(BaseModel):
    action: str | None = None
    review_status: str | None = Field(default=None, alias="reviewStatus")
    status: str | None = None
    current_stage: str | None = Field(default=None, alias="currentStage")
    stage: str | None = None
    review_comment: str | None = Field(default=None, alias="reviewComment")
    comment: str | None = None
    collection_id: str | None = Field(default=None, alias="collectionId")
    config_json: Any | None = Field(default=None, alias="configJson")
    revision_instruction: str | None = Field(default=None, alias="revisionInstruction")
    result_yaml: str | None = Field(default=None, alias="resultYaml")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        json_schema_extra={"additionalProperties": False},
    )


class AiGenerateTaskResponse(BaseModel):
    task_id: str = Field(alias="taskId")
    task_type: str = Field(alias="taskType")
    name: str
    project_id: str = Field(alias="projectId")
    sprint_id: str = Field(alias="sprintId")
    requirement_id: str = Field(alias="requirementId")
    creator_user_id: str = Field(alias="creatorUserId")
    source_type: str = Field(alias="sourceType")
    source_content: str = Field(alias="sourceContent")
    instruction: str = ""

    model_config = ConfigDict(populate_by_name=True)


class ImportedTarget(BaseModel):
    target_type: Literal["api_collection", "function_suite", "ui_suite"] = Field(
        alias="targetType"
    )
    target_id: str = Field(alias="targetId")

    model_config = ConfigDict(populate_by_name=True)


class AiGenerateTaskRunResponse(BaseModel):
    run_id: str = Field(alias="runId")
    task_id: str = Field(alias="taskId")
    requirement_id: str = Field(alias="requirementId")
    sprint_id: str = Field(alias="sprintId")
    project_id: str = Field(alias="projectId")
    trigger_user_id: str = Field(alias="triggerUserId")
    trigger_type: str = Field(alias="triggerType")
    status: str
    checkpoint_enabled: bool = Field(alias="checkpointEnabled")
    current_stage: str = Field(alias="currentStage")
    stage_status: str = Field(alias="stageStatus")
    snapshot_json: Any = Field(default_factory=dict, alias="snapshotJson")
    error_message: str = Field(alias="errorMessage")
    config_json: Any = Field(default_factory=dict, alias="configJson")
    result_yaml: str = Field(alias="resultYaml")
    result_summary_json: Any = Field(default_factory=dict, alias="resultSummaryJson")
    review_status: str = Field(alias="reviewStatus")
    imported_collection_id: str = Field(alias="importedCollectionId")
    import_status: Literal["pending", "imported"] = Field(alias="importStatus")
    imported_targets: list[ImportedTarget] = Field(default_factory=list, alias="importedTargets")
    imported_at: datetime | str | None = Field(default=None, alias="importedAt")
    import_migration_complete: bool = Field(alias="importMigrationComplete")
    reviewer_user_id: str = Field(alias="reviewerUserId")
    reviewed_at: datetime | str | None = Field(default=None, alias="reviewedAt")
    review_comment: str = Field(alias="reviewComment")
    duration_ms: int = Field(alias="durationMs")

    model_config = ConfigDict(populate_by_name=True)


