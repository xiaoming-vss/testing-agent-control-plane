from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CreateZentaoIntegrationConnectionRequest(BaseModel):
    name: str
    base_url: str = Field(alias="baseUrl")
    account: str
    password: str

    model_config = ConfigDict(populate_by_name=True)


class UpdateZentaoIntegrationConnectionRequest(BaseModel):
    name: str | None = None
    base_url: str | None = Field(default=None, alias="baseUrl")
    account: str | None = None
    password: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class CreateLLMIntegrationConnectionRequest(BaseModel):
    name: str
    base_url: str = Field(alias="baseUrl")
    model_id: str = Field(alias="modelId")
    api_key: str = Field(alias="apiKey")

    model_config = ConfigDict(populate_by_name=True)


class UpdateLLMIntegrationConnectionRequest(BaseModel):
    name: str | None = None
    base_url: str | None = Field(default=None, alias="baseUrl")
    model_id: str | None = Field(default=None, alias="modelId")
    api_key: str | None = Field(default=None, alias="apiKey")

    model_config = ConfigDict(populate_by_name=True)


class IntegrationConnectionResponse(BaseModel):
    connection_id: str = Field(alias="connectionId")
    provider: str
    name: str
    base_url: str = Field(alias="baseUrl")
    auth_type: str = Field(alias="authType")
    account: str = ""
    status: str
    has_access_token: bool = Field(alias="hasAccessToken")
    model_id: str = Field(default="", alias="modelId")
    token_expires_at: datetime | str | None = Field(default=None, alias="tokenExpiresAt")
    last_auth_at: datetime | str | None = Field(default=None, alias="lastAuthAt")
    last_auth_error: str = Field(default="", alias="lastAuthError")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")

    model_config = ConfigDict(populate_by_name=True)


class RemoteResourceListResponse(BaseModel):
    connection_id: str = Field(alias="connectionId")
    remote_project_id: str | None = Field(default=None, alias="remoteProjectId")
    remote_execution_id: str | None = Field(default=None, alias="remoteExecutionId")
    items: list[Any]
    total: int = 0

    model_config = ConfigDict(populate_by_name=True)
