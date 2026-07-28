from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TestMetricGroup(BaseModel):
    total: int = 0
    executed: int = 0
    pending: int = 0
    success: int = 0
    failed: int = 0


class BugMetricGroup(BaseModel):
    total: int = 0
    resolved: int = 0
    unresolved: int = 0
    fatal: int = 0
    serious: int = 0
    normal: int = 0
    suggestion: int = 0


class ProjectMetricContext(BaseModel):
    project_name: str = Field(default="", alias="projectName")
    description: str = ""

    model_config = ConfigDict(populate_by_name=True)


class SprintMetricContext(BaseModel):
    sprint_name: str = Field(default="", alias="sprintName")
    start_date: str = Field(default="", alias="startDate")
    end_date: str = Field(default="", alias="endDate")
    description: str = ""

    model_config = ConfigDict(populate_by_name=True)


class RequirementMetricContext(BaseModel):
    requirement_name: str = Field(default="", alias="requirementName")
    description: str = ""

    model_config = ConfigDict(populate_by_name=True)


class BugDetailContext(BaseModel):
    title: str = ""
    module: str = ""
    severity: str = ""
    status: str = ""
    owner: str = ""
    description: str = ""


class SprintDailyMetricRequest(BaseModel):
    function_case_total: int | None = Field(default=None, alias="functionCaseTotal")
    function_case_executed: int | None = Field(default=None, alias="functionCaseExecuted")
    function_case_pending: int | None = Field(default=None, alias="functionCasePending")
    function_case_success: int | None = Field(default=None, alias="functionCaseSuccess")
    function_case_failed: int | None = Field(default=None, alias="functionCaseFailed")
    api_case_total: int | None = Field(default=None, alias="apiCaseTotal")
    api_case_executed: int | None = Field(default=None, alias="apiCaseExecuted")
    api_case_pending: int | None = Field(default=None, alias="apiCasePending")
    api_case_success: int | None = Field(default=None, alias="apiCaseSuccess")
    api_case_failed: int | None = Field(default=None, alias="apiCaseFailed")
    ui_case_total: int | None = Field(default=None, alias="uiCaseTotal")
    ui_case_executed: int | None = Field(default=None, alias="uiCaseExecuted")
    ui_case_pending: int | None = Field(default=None, alias="uiCasePending")
    ui_case_success: int | None = Field(default=None, alias="uiCaseSuccess")
    ui_case_failed: int | None = Field(default=None, alias="uiCaseFailed")
    bug_total: int | None = Field(default=None, alias="bugTotal")
    bug_resolved: int | None = Field(default=None, alias="bugResolved")
    bug_unresolved: int | None = Field(default=None, alias="bugUnresolved")
    bug_fatal: int | None = Field(default=None, alias="bugFatal")
    bug_serious: int | None = Field(default=None, alias="bugSerious")
    bug_normal: int | None = Field(default=None, alias="bugNormal")
    bug_suggestion: int | None = Field(default=None, alias="bugSuggestion")

    model_config = ConfigDict(populate_by_name=True)


class SprintDailyMetricResponse(BaseModel):
    project_id: str = Field(alias="projectId")
    sprint_id: str = Field(alias="sprintId")
    snapshot_date: str = Field(alias="snapshotDate")
    function: TestMetricGroup
    api: TestMetricGroup
    ui: TestMetricGroup
    bug: BugMetricGroup
    project: ProjectMetricContext = Field(default_factory=ProjectMetricContext)
    sprint: SprintMetricContext = Field(default_factory=SprintMetricContext)
    requirements: list[RequirementMetricContext] = Field(default_factory=list)
    bugs: list[BugDetailContext] = Field(default_factory=list)
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")

    model_config = ConfigDict(populate_by_name=True)
