from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from testing_agent.core.errors import ErrNotFound
from testing_agent.core.sid import new_id
from testing_agent.models.integration_connection import IntegrationConnection
from testing_agent.repositories.integration_connection import IntegrationConnectionRepository


def dump_connection(connection: IntegrationConnection) -> dict[str, Any]:
    extra = connection.extra_json or {}
    secret = getattr(connection, "secret_json", None) or {}
    model_id = extra.get("modelId") or extra.get("model_id") or secret.get("modelId") or ""
    return {
        "connectionId": connection.connection_id,
        "provider": connection.provider,
        "name": connection.name,
        "baseUrl": connection.base_url,
        "authType": connection.auth_type,
        "account": connection.account,
        "status": connection.status,
        "hasAccessToken": bool(connection.access_token or secret.get("apiKey")),
        "modelId": model_id,
        "tokenExpiresAt": getattr(connection, "token_expires_at", None),
        "lastAuthAt": connection.last_auth_at,
        "lastAuthError": connection.last_auth_error,
        "createdAt": connection.created_at,
        "updatedAt": connection.updated_at,
    }


class IntegrationConnectionService:
    def __init__(self, repository: IntegrationConnectionRepository):
        self.repository = repository

    async def get_owned(
        self, user_id: str, provider: str, connection_id: str
    ) -> IntegrationConnection:
        connection = await self.repository.get(user_id, provider, connection_id)
        if connection is None:
            raise ErrNotFound
        return connection

    async def create(self, provider: str, body: dict[str, Any], user_id: str) -> dict:
        if provider == "zentao":
            secret_json = {"password": body.get("password", "")}
            extra_json: dict[str, Any] = {}
            auth_type = "password"
            access_token = str(body.get("accessToken") or "")
        else:
            secret_json = {"apiKey": body.get("apiKey", "")}
            extra_json = {"modelId": body.get("modelId", "")}
            auth_type = "api_key"
            access_token = str(body.get("apiKey") or "")
        connection = IntegrationConnection(
            connection_id=new_id(),
            user_id=user_id,
            provider=provider,
            name=str(body.get("name") or f"{provider}-connection"),
            base_url=str(body.get("baseUrl") or ""),
            auth_type=auth_type,
            account=str(body.get("account") or ""),
            secret_json=secret_json,
            access_token=access_token,
            refresh_token=str(body.get("refreshToken") or ""),
            status=str(body.get("status") or "active"),
            extra_json=extra_json,
        )
        self.repository.add(connection)
        await self.repository.commit()
        await self.repository.refresh(connection)
        return dump_connection(connection)

    async def list(self, provider: str, user_id: str) -> list[dict]:
        rows = await self.repository.list(user_id, provider)
        return [dump_connection(row) for row in rows]

    async def get(self, provider: str, connection_id: str, user_id: str) -> dict:
        return dump_connection(await self.get_owned(user_id, provider, connection_id))

    async def update(
        self, provider: str, connection_id: str, body: dict[str, Any], user_id: str
    ) -> dict:
        connection = await self.get_owned(user_id, provider, connection_id)
        for key, attr in {"name": "name", "baseUrl": "base_url", "account": "account"}.items():
            if key in body:
                setattr(connection, attr, body[key])
        if "password" in body:
            secret = dict(connection.secret_json or {})
            secret["password"] = body["password"]
            connection.secret_json = secret
        if "apiKey" in body:
            secret = dict(connection.secret_json or {})
            secret["apiKey"] = body["apiKey"]
            connection.secret_json = secret
            connection.access_token = body["apiKey"]
        if "modelId" in body:
            extra = dict(connection.extra_json or {})
            extra["modelId"] = body["modelId"]
            connection.extra_json = extra
        await self.repository.commit()
        await self.repository.refresh(connection)
        return dump_connection(connection)

    async def reauth_zentao(
        self,
        connection_id: str,
        body: dict[str, Any] | None,
        user_id: str,
    ) -> dict:
        connection = await self.get_owned(user_id, "zentao", connection_id)
        connection.status = "active"
        connection.last_auth_at = datetime.now(UTC)
        connection.last_auth_error = ""
        if body and body.get("password"):
            secret = connection.secret_json or {}
            secret["password"] = body["password"]
            connection.secret_json = secret
        await self.repository.commit()
        await self.repository.refresh(connection)
        return dump_connection(connection)

    async def delete(self, provider: str, connection_id: str, user_id: str) -> dict:
        connection = await self.get_owned(user_id, provider, connection_id)
        connection.deleted_at = datetime.now(UTC)
        connection.status = "deleted"
        await self.repository.commit()
        return {}

    async def list_remote(
        self,
        provider: str,
        connection_id: str,
        user_id: str,
        **extra: str,
    ) -> dict:
        await self.get_owned(user_id, provider, connection_id)
        return {"connectionId": connection_id, **extra, "items": []}
