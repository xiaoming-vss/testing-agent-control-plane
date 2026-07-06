from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from testing_agent.core.errors import ErrForbidden, ErrNotFound
from testing_agent.core.sid import new_id
from testing_agent.models.resource_binding import ResourceBinding
from testing_agent.repositories.resource_binding import ResourceBindingRepository


def dump_binding(binding: ResourceBinding) -> dict[str, Any]:
    return {
        "bindingId": binding.binding_id,
        "provider": binding.provider,
        "connectionId": binding.connection_id,
        "localResourceType": binding.local_resource_type,
        "localResourceId": binding.local_resource_id,
        "remoteResourceType": binding.remote_resource_type,
        "remoteResourceId": binding.remote_resource_id,
        "remoteParentId": binding.remote_parent_id,
        "remoteNameSnapshot": binding.remote_name_snapshot,
        "status": binding.status,
        "boundAt": binding.bound_at,
        "lastVerifiedAt": binding.last_verified_at,
        "lastSyncError": binding.last_sync_error,
        "createdAt": binding.created_at,
        "updatedAt": binding.updated_at,
    }


class ResourceBindingService:
    def __init__(self, repository: ResourceBindingRepository):
        self.repository = repository

    async def ensure_local_owner(
        self, user_id: str, resource_type: str, resource_id: str
    ) -> str:
        if resource_type == "project":
            project = await self.repository.get_project(resource_id)
            if project is None:
                raise ErrNotFound
            if project.user_id != user_id:
                raise ErrForbidden
            return resource_id
        if resource_type == "sprint":
            sprint = await self.repository.get_sprint(resource_id)
            if sprint is None:
                raise ErrNotFound
            await self.ensure_local_owner(user_id, "project", sprint.project_id)
            return sprint.project_id
        if resource_type == "requirement":
            requirement = await self.repository.get_requirement(resource_id)
            if requirement is None:
                raise ErrNotFound
            sprint = await self.repository.get_sprint(requirement.sprint_id)
            if sprint is None:
                raise ErrNotFound
            await self.ensure_local_owner(user_id, "project", sprint.project_id)
            return sprint.project_id
        raise ErrNotFound

    async def create(
        self, resource_type: str, resource_id: str, body: dict[str, Any], user_id: str
    ) -> dict:
        await self.ensure_local_owner(user_id, resource_type, resource_id)
        binding = ResourceBinding(
            binding_id=new_id(),
            user_id=user_id,
            provider=str(body.get("provider") or "zentao"),
            connection_id=str(body.get("connectionId") or body.get("connection_id") or ""),
            local_resource_type=resource_type,
            local_resource_id=resource_id,
            remote_resource_type=str(
                body.get("remoteResourceType") or body.get("remote_resource_type") or resource_type
            ),
            remote_resource_id=str(
                body.get("remoteResourceId") or body.get("remote_resource_id") or ""
            ),
            remote_parent_id=str(body.get("remoteParentId") or body.get("remote_parent_id") or ""),
            remote_name_snapshot=str(
                body.get("remoteNameSnapshot") or body.get("remote_name_snapshot") or ""
            ),
            status="active",
            bound_at=datetime.now(UTC),
            extra_json=body.get("extraJson") or body.get("extra_json") or {},
        )
        self.repository.add(binding)
        await self.repository.commit()
        await self.repository.refresh(binding)
        return dump_binding(binding)

    async def list(self, resource_type: str, resource_id: str, user_id: str) -> list[dict]:
        await self.ensure_local_owner(user_id, resource_type, resource_id)
        rows = await self.repository.list(user_id, resource_type, resource_id)
        return [dump_binding(row) for row in rows]

    async def delete(
        self, resource_type: str, resource_id: str, binding_id: str, user_id: str
    ) -> dict:
        await self.ensure_local_owner(user_id, resource_type, resource_id)
        binding = await self.repository.get(resource_type, resource_id, binding_id)
        if binding is None:
            raise ErrNotFound
        if binding.user_id != user_id:
            raise ErrForbidden
        binding.status = "unbound"
        binding.deleted_at = datetime.now(UTC)
        await self.repository.commit()
        return {}
