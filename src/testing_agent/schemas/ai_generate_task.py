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


class AiGenerateTaskResultRequest(BaseModel):
    result_yaml: str = Field(alias="resultYaml")

    model_config = ConfigDict(populate_by_name=True)


class AiGenerateTaskImportRequest(BaseModel):
    collection_id: str = Field(alias="collectionId")
    confirm_overwrite: bool = Field(default=False, alias="confirmOverwrite")

    model_config = ConfigDict(populate_by_name=True)


class FunctionGenerateTaskImportRequest(BaseModel):
    confirm_overwrite: bool = Field(default=False, alias="confirmOverwrite")

    model_config = ConfigDict(populate_by_name=True)


class UiGenerateTaskImportRequest(BaseModel):
    suite_id: str = Field(alias="suiteId")
    confirm_overwrite: bool = Field(default=False, alias="confirmOverwrite")

    model_config = ConfigDict(populate_by_name=True)


class SourceArchiveResponse(BaseModel):
    archive_id: str = Field(alias="archiveId")
    filename: str
    size_bytes: int = Field(alias="sizeBytes")
    sha256: str
    uploaded_at: datetime = Field(alias="uploadedAt")

    model_config = ConfigDict(populate_by_name=True)


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
    source_archive: SourceArchiveResponse | None = Field(default=None, alias="sourceArchive")
    instruction: str = ""
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")

    model_config = ConfigDict(populate_by_name=True)


class ImportedTarget(BaseModel):
    target_type: Literal["api_collection", "function_suite", "ui_suite"] = Field(alias="targetType")
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
    import_status: Literal["pending", "imported"] = Field(alias="importStatus")
    imported_targets: list[ImportedTarget] = Field(default_factory=list, alias="importedTargets")
    imported_at: datetime | str | None = Field(default=None, alias="importedAt")
    import_migration_complete: bool = Field(alias="importMigrationComplete")
    reviewer_user_id: str = Field(alias="reviewerUserId")
    reviewed_at: datetime | str | None = Field(default=None, alias="reviewedAt")
    review_comment: str = Field(alias="reviewComment")
    duration_ms: int = Field(alias="durationMs")

    model_config = ConfigDict(populate_by_name=True)


class ApiCaseExtractRuleComparison(BaseModel):
    name: str
    enabled: bool
    order_no: int = Field(alias="orderNo")
    source: str
    source_expr: str = Field(alias="sourceExpr")
    var_key: str = Field(alias="varKey")
    default_value: str = Field(alias="defaultValue")

    model_config = ConfigDict(populate_by_name=True)


class ApiCaseAssertRuleComparison(BaseModel):
    name: str
    enabled: bool
    order_no: int = Field(alias="orderNo")
    assert_source: str = Field(alias="assertSource")
    target_expr: str = Field(alias="targetExpr")
    comparator: str
    expected_value: str = Field(alias="expectedValue")

    model_config = ConfigDict(populate_by_name=True)


class ApiCaseComparison(BaseModel):
    name: str
    description: str
    enabled: bool
    order_no: int = Field(alias="orderNo")
    method: str
    url_template: str = Field(alias="urlTemplate")
    headers: Any
    query: Any
    body_type: str = Field(alias="bodyType")
    body_json: Any = Field(alias="bodyJson")
    body_text: str = Field(alias="bodyText")
    timeout_ms: int = Field(alias="timeoutMs")
    continue_on_failure: bool = Field(alias="continueOnFailure")
    extract_rules: list[ApiCaseExtractRuleComparison] = Field(alias="extractRules")
    assert_rules: list[ApiCaseAssertRuleComparison] = Field(alias="assertRules")

    model_config = ConfigDict(populate_by_name=True)


class ApiCaseImportConflict(BaseModel):
    normalized_name: str = Field(alias="normalizedName")
    existing_case: ApiCaseComparison = Field(alias="existingCase")
    generated_case: ApiCaseComparison = Field(alias="generatedCase")

    model_config = ConfigDict(populate_by_name=True)


class AiGenerateTaskImportResponse(BaseModel):
    requires_confirmation: bool = Field(alias="requiresConfirmation")
    conflicts: list[ApiCaseImportConflict] = Field(default_factory=list)
    run: AiGenerateTaskRunResponse

    model_config = ConfigDict(populate_by_name=True)


class FunctionCaseComparison(BaseModel):
    module: str
    title: str
    preconditions: str
    steps: str
    expected_results: str = Field(alias="expectedResults")
    priority: str
    case_type: str = Field(alias="caseType")

    model_config = ConfigDict(populate_by_name=True)


class FunctionCaseImportConflict(BaseModel):
    normalized_name: str = Field(alias="normalizedName")
    existing_case: FunctionCaseComparison = Field(alias="existingCase")
    generated_case: FunctionCaseComparison = Field(alias="generatedCase")

    model_config = ConfigDict(populate_by_name=True)


class FunctionGenerateTaskImportResponse(BaseModel):
    requires_confirmation: bool = Field(alias="requiresConfirmation")
    conflicts: list[FunctionCaseImportConflict] = Field(default_factory=list)
    run: AiGenerateTaskRunResponse

    model_config = ConfigDict(populate_by_name=True)


class UiCaseComparison(BaseModel):
    name: str
    enabled: bool
    order_no: int = Field(alias="orderNo")
    steps_json: Any = Field(alias="stepsJson")

    model_config = ConfigDict(populate_by_name=True)


class UiCaseImportConflict(BaseModel):
    normalized_name: str = Field(alias="normalizedName")
    existing_case: UiCaseComparison = Field(alias="existingCase")
    generated_case: UiCaseComparison = Field(alias="generatedCase")

    model_config = ConfigDict(populate_by_name=True)


class UiGenerateTaskImportResponse(BaseModel):
    requires_confirmation: bool = Field(alias="requiresConfirmation")
    conflicts: list[UiCaseImportConflict] = Field(default_factory=list)
    run: AiGenerateTaskRunResponse

    model_config = ConfigDict(populate_by_name=True)
