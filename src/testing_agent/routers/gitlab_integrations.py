from __future__ import annotations

from fastapi import APIRouter

from testing_agent.handlers.integration_connection import (
    create_gitlab_connection,
    delete_gitlab_connection,
    get_gitlab_connection,
    list_gitlab_connections,
    reauth_gitlab_connection,
    update_gitlab_connection,
)
from testing_agent.schemas.common import ApiResponse, EmptyData, ListResponse
from testing_agent.schemas.integrations import IntegrationConnectionResponse

router = APIRouter()

router.post(
    "/integrations/gitlab/connections",
    response_model=ApiResponse[IntegrationConnectionResponse],
)(create_gitlab_connection)
router.get(
    "/integrations/gitlab/connections",
    response_model=ApiResponse[ListResponse[IntegrationConnectionResponse]],
)(list_gitlab_connections)
router.get(
    "/integrations/gitlab/connections/{connection_id}",
    response_model=ApiResponse[IntegrationConnectionResponse],
)(get_gitlab_connection)
router.patch(
    "/integrations/gitlab/connections/{connection_id}",
    response_model=ApiResponse[IntegrationConnectionResponse],
)(update_gitlab_connection)
router.post(
    "/integrations/gitlab/connections/{connection_id}/reauth",
    response_model=ApiResponse[IntegrationConnectionResponse],
)(reauth_gitlab_connection)
router.delete(
    "/integrations/gitlab/connections/{connection_id}",
    response_model=ApiResponse[EmptyData],
)(delete_gitlab_connection)
