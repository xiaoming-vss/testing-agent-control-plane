from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from testing_agent.core.errors import (
    ErrBadRequest,
    ErrForbidden,
    ErrIntegrationConnectionNotFound,
    ErrNotFound,
    ErrRemoteResourceAlreadyBound,
    ErrResourceBindingAlreadyExists,
    ErrResourceBindingInvalid,
    ErrZentaoRemoteResourceUnavailable,
    dynamic_error,
)
from testing_agent.core.sid import new_id
from testing_agent.models.resource_binding import ResourceBinding
from testing_agent.repositories.resource_binding import ResourceBindingRepository
from testing_agent.services.common import list_payload
from testing_agent.services.integration_connection import IntegrationConnectionService
from testing_agent.services.zentao_resource import parse_zentao_remote_id, truncate_error


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


ZENTAO_REMOTE_TYPE_DEFAULTS = {
    "project": "project",
    "sprint": "execution",
    "requirement": "story",
}


class ResourceBindingService:
    def __init__(
        self,
        repository: ResourceBindingRepository,
        integration_connection_service: IntegrationConnectionService | None = None,
        zentao_resource_client: Any | None = None,
    ):
        self.repository = repository
        self.integration_connection_service = integration_connection_service
        self.zentao_resource_client = zentao_resource_client

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
        if resource_type == "project":
            return await self._create_project_binding(resource_id, body, user_id)

        await self.ensure_local_owner(user_id, resource_type, resource_id)
        binding = ResourceBinding(
            binding_id=new_id(),
            user_id=user_id,
            provider=str(body.get("provider") or "zentao"),
            connection_id=str(body.get("connectionId") or body.get("connection_id") or ""),
            local_resource_type=resource_type,
            local_resource_id=resource_id,
            remote_resource_type=str(
                body.get("remoteResourceType")
                or body.get("remote_resource_type")
                or ZENTAO_REMOTE_TYPE_DEFAULTS.get(resource_type, resource_type)
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

    async def _create_project_binding(
        self,
        project_id: str,
        body: dict[str, Any],
        user_id: str,
    ) -> dict:
        project = await self.repository.get_project(project_id)
        if project is None:
            raise ErrNotFound
        if project.user_id != user_id:
            raise ErrForbidden

        provider = str(body.get("provider") or "zentao").strip()
        connection_id = str(body.get("connectionId") or body.get("connection_id") or "").strip()
        remote_resource_id = str(
            body.get("remoteResourceId") or body.get("remote_resource_id") or ""
        ).strip()
        if provider != "zentao" or not connection_id or not remote_resource_id:
            raise ErrBadRequest
        try:
            parse_zentao_remote_id(remote_resource_id)
        except ValueError as exc:
            raise dynamic_error(ErrResourceBindingInvalid, str(exc)) from exc

        existing_local = await self.repository.get_active_by_local_resource("project", project_id)
        if existing_local is not None:
            raise ErrResourceBindingAlreadyExists

        if self.integration_connection_service is None:
            raise ErrIntegrationConnectionNotFound
        connection = await self.integration_connection_service.get_owned(
            user_id,
            "zentao",
            connection_id,
        )

        if self.zentao_resource_client is None:
            raise ErrZentaoRemoteResourceUnavailable
        try:
            remote_project = await self.zentao_resource_client.get_project(
                connection,
                remote_resource_id,
            )
        except Exception as exc:
            raise dynamic_error(
                ErrZentaoRemoteResourceUnavailable,
                truncate_error(str(exc)),
            ) from exc
        if bool(getattr(remote_project, "deleted", False)):
            raise dynamic_error(ErrZentaoRemoteResourceUnavailable, "禅道项目已删除")

        remote_project_id = str(int(remote_project.id))
        remote_exists = await self.repository.exists_active_by_remote_resource(
            provider,
            connection_id,
            "project",
            remote_project_id,
        )
        if remote_exists:
            raise ErrRemoteResourceAlreadyBound

        now = datetime.now(UTC)
        binding = ResourceBinding(
            binding_id=new_id(),
            user_id=user_id,
            provider=provider,
            connection_id=connection_id,
            local_resource_type="project",
            local_resource_id=project_id,
            remote_resource_type="project",
            remote_resource_id=remote_project_id,
            remote_parent_id="",
            remote_name_snapshot=str(getattr(remote_project, "name", "") or ""),
            status="active",
            bound_at=now,
            last_verified_at=now,
            last_sync_error="",
            extra_json={},
        )
        self.repository.add(binding)
        project.source_type = "bound"
        project.binding_status = "bound"
        project.last_bound_at = now
        project.last_binding_sync_error = ""
        await self.repository.commit()
        await self.repository.refresh(binding)
        return dump_binding(binding)

    async def list(self, resource_type: str, resource_id: str, user_id: str) -> dict[str, Any]:
        await self.ensure_local_owner(user_id, resource_type, resource_id)
        rows = await self.repository.list(user_id, resource_type, resource_id)
        return list_payload([dump_binding(row) for row in rows])

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
