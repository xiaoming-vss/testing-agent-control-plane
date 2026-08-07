from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


def parse_json_object(value: Any) -> dict[str, Any] | None:
    if value is None or isinstance(value, dict):
        return value
    if isinstance(value, str):
        if not value.strip():
            return {}
        parsed = json.loads(value)
        if isinstance(parsed, dict):
            return parsed
    raise ValueError("Input should be a valid dictionary or JSON object string")


def accept_worker_json_text(value: Any) -> Any:
    if isinstance(value, str):
        if not value.strip():
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


class WorkerClaimRequest(BaseModel):
    worker_id: str = Field(alias="workerId")

    model_config = ConfigDict(populate_by_name=True)


class WorkerTaskData(BaseModel):
    task_id: str = Field(alias="taskId")
    task_type: str = Field(alias="taskType")
    run_id: str = Field(alias="runId")
    status: str

    model_config = ConfigDict(populate_by_name=True)


class WorkerClaimResponse(BaseModel):
    task: dict[str, Any] | None = None


class WorkerClaimPayload(BaseModel):
    task_id: str = Field(alias="taskId")
    task_type: str = Field(alias="taskType")
    run_id: str = Field(alias="runId")
    domain: str | None = None
    suite_id: str | None = Field(default=None, alias="suiteId")
    case_id: str | None = Field(default=None, alias="caseId")
    collection_run_id: str | None = Field(default=None, alias="collectionRunId")
    collection_id: str | None = Field(default=None, alias="collectionId")
    generate_task_id: str | None = Field(default=None, alias="generateTaskId")
    project_id: str | None = Field(default=None, alias="projectId")
    sprint_id: str | None = Field(default=None, alias="sprintId")
    requirement_id: str | None = Field(default=None, alias="requirementId")
    llm_connection_id: str | None = Field(default=None, alias="llmConnectionId")
    status: str | None = None
    checkpoint_enabled: bool | None = Field(default=None, alias="checkpointEnabled")
    current_stage: str | None = Field(default=None, alias="currentStage")
    config_json: str | None = Field(default=None, alias="configJson")
    lease_seconds: int | None = Field(default=None, alias="leaseSeconds")

    model_config = ConfigDict(populate_by_name=True)


class WorkerSnapshotResponse(BaseModel):
    task_type: str | None = Field(default=None, alias="taskType")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        json_schema_extra={"additionalProperties": False},
    )


class WorkerTaskAckResponse(BaseModel):
    task_id: str = Field(alias="taskId")
    worker_id: str | None = Field(default=None, alias="workerId")
    status: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class WorkerItemAckResponse(WorkerTaskAckResponse):
    item_id: str = Field(alias="itemId")


class WorkerProjectSkillResponse(BaseModel):
    skill_space_id: str = Field(alias="skillSpaceId")
    project_id: str = Field(alias="projectId")
    version: int
    hash: str
    download_url: str = Field(alias="downloadUrl")
    filename: str
    size: int
    is_default: bool = Field(alias="isDefault")

    model_config = ConfigDict(populate_by_name=True)


class WorkerProjectSkillsResponse(BaseModel):
    project_id: str = Field(alias="projectId")
    skills: list[WorkerProjectSkillResponse]

    model_config = ConfigDict(populate_by_name=True)


class WorkerLlmCredentialsResponse(BaseModel):
    task_id: str = Field(alias="taskId")
    connection_id: str | None = Field(default=None, alias="connectionId")
    base_url: str = Field(alias="baseUrl")
    model_id: str = Field(alias="modelId")
    api_key: str = Field(alias="apiKey")
    organization: str = ""

    model_config = ConfigDict(populate_by_name=True)


class WorkerProgressRequest(BaseModel):
    worker_id: str = Field(alias="workerId")
    task_id: str | None = Field(default=None, alias="taskId")
    run_id: str | None = Field(default=None, alias="runId")
    current_stage: str | None = Field(default=None, alias="currentStage")
    stage_status: str | None = Field(default=None, alias="stageStatus")
    config_json: Any | None = Field(default=None, alias="configJson")
    result_yaml: str | None = Field(default=None, alias="resultYaml")
    output_yaml: str | None = Field(default=None, alias="outputYaml")
    result_summary_json: Any | None = Field(default=None, alias="resultSummaryJson")
    error_message: str | None = Field(default=None, alias="errorMessage")

    model_config = ConfigDict(populate_by_name=True)

    _accept_config_json = field_validator("config_json", mode="before")(accept_worker_json_text)
    _parse_result_summary_json = field_validator("result_summary_json", mode="before")(
        accept_worker_json_text
    )


class WorkerTaskEventRequest(BaseModel):
    worker_id: str = Field(alias="workerId")
    task_id: str | None = Field(default=None, alias="taskId")
    run_id: str | None = Field(default=None, alias="runId")
    collection_run_id: str | None = Field(default=None, alias="collectionRunId")
    collection_id: str | None = Field(default=None, alias="collectionId")
    case_id: str | None = Field(default=None, alias="caseId")
    started_at: str | None = Field(default=None, alias="startedAt")
    heartbeat_at: str | None = Field(default=None, alias="heartbeatAt")
    finished_at: str | None = Field(default=None, alias="finishedAt")
    status: str | None = None
    success: bool | None = None
    error_message: str | None = Field(default=None, alias="errorMessage")
    duration_ms: int | None = Field(default=None, alias="durationMs")
    snapshot_json: Any | None = Field(default=None, alias="snapshotJson")
    step_results: list[Any] | None = Field(default=None, alias="stepResults")
    request: Any | None = None
    response: Any | None = None
    runtime_vars_json: Any | None = Field(default=None, alias="runtimeVarsJson")
    extract_results: list[Any] | None = Field(default=None, alias="extractResults")
    assert_results: list[Any] | None = Field(default=None, alias="assertResults")
    config_json: Any | None = Field(default=None, alias="configJson")
    result_yaml: str | None = Field(default=None, alias="resultYaml")
    output_yaml: str | None = Field(default=None, alias="outputYaml")
    result_summary_json: Any | None = Field(default=None, alias="resultSummaryJson")

    model_config = ConfigDict(populate_by_name=True)

    _parse_snapshot_json = field_validator("snapshot_json", mode="before")(parse_json_object)
    _parse_runtime_vars_json = field_validator("runtime_vars_json", mode="before")(
        parse_json_object
    )
    _accept_config_json = field_validator("config_json", mode="before")(accept_worker_json_text)
    _accept_result_summary_json = field_validator("result_summary_json", mode="before")(
        accept_worker_json_text
    )
