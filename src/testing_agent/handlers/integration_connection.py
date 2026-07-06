from __future__ import annotations

from fastapi import Depends

from testing_agent.api.deps import get_current_user_id, get_integration_connection_service
from testing_agent.core.errors import success_payload
from testing_agent.schemas.integrations import (
    CreateLLMIntegrationConnectionRequest,
    CreateZentaoIntegrationConnectionRequest,
    UpdateLLMIntegrationConnectionRequest,
    UpdateZentaoIntegrationConnectionRequest,
)
from testing_agent.services.integration_connection import IntegrationConnectionService


async def create_zentao_connection(
    body: CreateZentaoIntegrationConnectionRequest,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    return success_payload(await service.create("zentao", body.model_dump(by_alias=True), user_id))


async def list_zentao_connections(
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    return success_payload(await service.list("zentao", user_id))


async def get_zentao_connection(
    connection_id: str,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    return success_payload(await service.get("zentao", connection_id, user_id))


async def update_zentao_connection(
    connection_id: str,
    body: UpdateZentaoIntegrationConnectionRequest,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    return success_payload(
        await service.update(
            "zentao",
            connection_id,
            body.model_dump(by_alias=True, exclude_none=True),
            user_id,
        )
    )


async def reauth_zentao_connection(
    connection_id: str,
    body: UpdateZentaoIntegrationConnectionRequest | None = None,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    payload = body.model_dump(by_alias=True, exclude_none=True) if body else None
    return success_payload(await service.reauth_zentao(connection_id, payload, user_id))


async def delete_zentao_connection(
    connection_id: str,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    return success_payload(await service.delete("zentao", connection_id, user_id))


async def list_zentao_projects(
    connection_id: str,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    return success_payload(await service.list_remote("zentao", connection_id, user_id))


async def list_zentao_project_executions(
    connection_id: str,
    remote_project_id: str,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    return success_payload(
        await service.list_remote(
            "zentao",
            connection_id,
            user_id,
            remoteProjectId=remote_project_id,
        )
    )


async def list_zentao_execution_testtasks(
    connection_id: str,
    remote_execution_id: str,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    return success_payload(
        await service.list_remote(
            "zentao",
            connection_id,
            user_id,
            remoteExecutionId=remote_execution_id,
        )
    )


async def list_zentao_execution_stories(
    connection_id: str,
    remote_execution_id: str,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    return success_payload(
        await service.list_remote(
            "zentao",
            connection_id,
            user_id,
            remoteExecutionId=remote_execution_id,
        )
    )


async def list_zentao_execution_cases(
    connection_id: str,
    remote_execution_id: str,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    return success_payload(
        await service.list_remote(
            "zentao",
            connection_id,
            user_id,
            remoteExecutionId=remote_execution_id,
        )
    )


async def create_llm_connection(
    body: CreateLLMIntegrationConnectionRequest,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    return success_payload(await service.create("llm", body.model_dump(by_alias=True), user_id))


async def list_llm_connections(
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    return success_payload(await service.list("llm", user_id))


async def get_llm_connection(
    connection_id: str,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    return success_payload(await service.get("llm", connection_id, user_id))


async def update_llm_connection(
    connection_id: str,
    body: UpdateLLMIntegrationConnectionRequest,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    return success_payload(
        await service.update(
            "llm",
            connection_id,
            body.model_dump(by_alias=True, exclude_none=True),
            user_id,
        )
    )


async def delete_llm_connection(
    connection_id: str,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationConnectionService = Depends(get_integration_connection_service),
):
    return success_payload(await service.delete("llm", connection_id, user_id))

