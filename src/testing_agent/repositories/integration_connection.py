from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.integration_connection import IntegrationConnection


class IntegrationConnectionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(
        self, user_id: str, provider: str, connection_id: str
    ) -> IntegrationConnection | None:
        return await self.session.scalar(
            select(IntegrationConnection).where(
                IntegrationConnection.connection_id == connection_id,
                IntegrationConnection.user_id == user_id,
                IntegrationConnection.provider == provider,
                IntegrationConnection.deleted_at.is_(None),
            )
        )

    async def list(self, user_id: str, provider: str) -> list[IntegrationConnection]:
        return list(
            (
                await self.session.scalars(
                    select(IntegrationConnection)
                    .where(
                        IntegrationConnection.user_id == user_id,
                        IntegrationConnection.provider == provider,
                        IntegrationConnection.deleted_at.is_(None),
                    )
                    .order_by(IntegrationConnection.created_at.desc())
                )
            ).all()
        )

    def add(self, connection: IntegrationConnection) -> None:
        self.session.add(connection)

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, connection: IntegrationConnection) -> None:
        await self.session.refresh(connection)
