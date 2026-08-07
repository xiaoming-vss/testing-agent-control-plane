from __future__ import annotations

from fastapi import APIRouter

from testing_agent.handlers.integration_connection import (
    create_project_gitlab_connection,
    delete_project_gitlab_connection,
    get_project_gitlab_connection,
    list_project_gitlab_connections,
    reauth_project_gitlab_connection,
    update_project_gitlab_connection,
)
from testing_agent.schemas.common import ApiResponse, EmptyData, ListResponse
from testing_agent.schemas.integrations import IntegrationConnectionResponse

router = APIRouter()

router.post(
    "/projects/{project_id}/integrations/gitlab/connections",
    response_model=ApiResponse[IntegrationConnectionResponse],
)(create_project_gitlab_connection)
router.get(
    "/projects/{project_id}/integrations/gitlab/connections",
    response_model=ApiResponse[ListResponse[IntegrationConnectionResponse]],
)(list_project_gitlab_connections)
router.get(
    "/projects/{project_id}/integrations/gitlab/connections/{connection_id}",
    response_model=ApiResponse[IntegrationConnectionResponse],
)(get_project_gitlab_connection)
router.patch(
    "/projects/{project_id}/integrations/gitlab/connections/{connection_id}",
    response_model=ApiResponse[IntegrationConnectionResponse],
)(update_project_gitlab_connection)
router.post(
    "/projects/{project_id}/integrations/gitlab/connections/{connection_id}/reauth",
    response_model=ApiResponse[IntegrationConnectionResponse],
)(reauth_project_gitlab_connection)
router.delete(
    "/projects/{project_id}/integrations/gitlab/connections/{connection_id}",
    response_model=ApiResponse[EmptyData],
)(delete_project_gitlab_connection)
