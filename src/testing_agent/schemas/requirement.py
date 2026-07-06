from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

DOCUMENT_TYPES = {"text", "docx"}
DOCUMENT_TYPE_ALIASES = {"txt": "text", "word": "docx"}


def normalize_document_type(value: str) -> str:
    normalized = DOCUMENT_TYPE_ALIASES.get(value, value)
    if normalized not in DOCUMENT_TYPES:
        raise ValueError("documentType must be text or docx")
    return normalized


class CreateRequirementRequest(BaseModel):
    name: str
    document_type: str = Field(default="text", alias="documentType")
    document_content: str = Field(default="", alias="documentContent")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, value: str) -> str:
        return normalize_document_type(value)


class UpdateRequirementRequest(BaseModel):
    name: str | None = None
    document_type: str | None = Field(default=None, alias="documentType")
    document_content: str | None = Field(default=None, alias="documentContent")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_document_type(value)


class RequirementResponse(BaseModel):
    requirement_id: str = Field(alias="requirementId")
    sprint_id: str = Field(alias="sprintId")
    name: str
    document_type: str = Field(default="text", alias="documentType")
    document_content: str = Field(default="", alias="documentContent")
    document_filename: str = Field(default="", alias="documentFilename")
    document_hash: str = Field(default="", alias="documentHash")
    document_download_url: str = Field(default="", alias="documentDownloadUrl")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, value: str) -> str:
        return normalize_document_type(value)
