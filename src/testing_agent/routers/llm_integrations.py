from __future__ import annotations

from fastapi import APIRouter

from testing_agent.handlers.integration_connection import (
    create_llm_connection,
    delete_llm_connection,
    get_llm_connection,
    list_llm_connections,
    update_llm_connection,
)
from testing_agent.schemas.common import ApiResponse, EmptyData, ListResponse
from testing_agent.schemas.integrations import IntegrationConnectionResponse

router = APIRouter()

router.post(
    "/integrations/llm/connections",
    response_model=ApiResponse[IntegrationConnectionResponse],
)(create_llm_connection)
router.get(
    "/integrations/llm/connections",
    response_model=ApiResponse[ListResponse[IntegrationConnectionResponse]],
)(list_llm_connections)
router.get(
    "/integrations/llm/connections/{connection_id}",
    response_model=ApiResponse[IntegrationConnectionResponse],
)(get_llm_connection)
router.patch(
    "/integrations/llm/connections/{connection_id}",
    response_model=ApiResponse[IntegrationConnectionResponse],
)(update_llm_connection)
router.delete(
    "/integrations/llm/connections/{connection_id}",
    response_model=ApiResponse[EmptyData],
)(delete_llm_connection)
