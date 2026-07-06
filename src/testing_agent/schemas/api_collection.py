from __future__ import annotations

# ruff: noqa: F401
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ApiCollectionRequest(BaseModel):
    name: str
    description: str = ""


class ApiCollectionUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None


class ApiCollectionResponse(BaseModel):
    collection_id: str = Field(alias="collectionId")
    requirement_id: str = Field(alias="requirementId")
    name: str
    description: str = ""
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ApiCollectionImportResponse(BaseModel):
    collection_id: str = Field(alias="collectionId")
    imported_case_count: int = Field(alias="importedCaseCount")
    imported_extract_rule_count: int = Field(alias="importedExtractRuleCount")
    imported_assert_rule_count: int = Field(alias="importedAssertRuleCount")
    model_config = ConfigDict(populate_by_name=True)
