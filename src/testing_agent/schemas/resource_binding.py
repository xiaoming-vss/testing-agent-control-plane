from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ResourceBindingRequest(BaseModel):
    provider: str = "zentao"
    connection_id: str = Field(alias="connectionId")
    remote_resource_type: str = Field(default="", alias="remoteResourceType")
    remote_resource_id: str = Field(alias="remoteResourceId")
    remote_parent_id: str = Field(default="", alias="remoteParentId")
    remote_name_snapshot: str = Field(default="", alias="remoteNameSnapshot")
    extra_json: Any | None = Field(default=None, alias="extraJson")

    model_config = ConfigDict(populate_by_name=True)


class ResourceBindingResponse(BaseModel):
    binding_id: str = Field(alias="bindingId")
    provider: str
    connection_id: str = Field(alias="connectionId")
    local_resource_type: str = Field(alias="localResourceType")
    local_resource_id: str = Field(alias="localResourceId")
    remote_resource_type: str = Field(alias="remoteResourceType")
    remote_resource_id: str = Field(alias="remoteResourceId")
    remote_parent_id: str = Field(default="", alias="remoteParentId")
    remote_name_snapshot: str = Field(default="", alias="remoteNameSnapshot")
    status: str
    bound_at: datetime | str | None = Field(default=None, alias="boundAt")
    last_verified_at: datetime | str | None = Field(default=None, alias="lastVerifiedAt")
    last_sync_error: str = Field(default="", alias="lastSyncError")
    created_at: datetime | str | None = Field(default="", alias="createdAt")
    updated_at: datetime | str | None = Field(default="", alias="updatedAt")

    model_config = ConfigDict(populate_by_name=True)
