from __future__ import annotations

# ruff: noqa: F401
import json
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

UiScreenshotPolicy = Literal["on_failure", "after_each_step", "never"]


class UiSuiteRequest(BaseModel):
    name: str
    description: str = ""
    headless: bool | None = None
    slow_mo_ms: int | None = Field(default=None, alias="slowMoMs")
    viewport_width: int | None = Field(default=None, alias="viewportWidth")
    viewport_height: int | None = Field(default=None, alias="viewportHeight")
    default_step_timeout_ms: int | None = Field(default=None, alias="defaultStepTimeoutMs")
    screenshot_policy: UiScreenshotPolicy = Field(default="on_failure", alias="screenshotPolicy")
    model_config = ConfigDict(populate_by_name=True)


class UiSuiteUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    headless: bool | None = None
    slow_mo_ms: int | None = Field(default=None, alias="slowMoMs")
    viewport_width: int | None = Field(default=None, alias="viewportWidth")
    viewport_height: int | None = Field(default=None, alias="viewportHeight")
    default_step_timeout_ms: int | None = Field(default=None, alias="defaultStepTimeoutMs")
    screenshot_policy: UiScreenshotPolicy | None = Field(default=None, alias="screenshotPolicy")
    model_config = ConfigDict(populate_by_name=True)


class UiSuiteResponse(UiSuiteRequest):
    suite_id: str = Field(alias="suiteId")
    requirement_id: str = Field(alias="requirementId")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
