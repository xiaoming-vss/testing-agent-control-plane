from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.ai_generate_task_source_archive import AiGenerateTaskSourceArchive


class AiGenerateTaskSourceArchiveRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_source_archive(self, task_id: str) -> AiGenerateTaskSourceArchive | None:
        return await self.session.scalar(
            select(AiGenerateTaskSourceArchive).where(
                AiGenerateTaskSourceArchive.task_id == task_id
            )
        )

    async def get_source_archive_for_update(
        self, task_id: str
    ) -> AiGenerateTaskSourceArchive | None:
        return await self.session.scalar(
            select(AiGenerateTaskSourceArchive)
            .where(AiGenerateTaskSourceArchive.task_id == task_id)
            .with_for_update()
        )

    def add(self, row: AiGenerateTaskSourceArchive) -> None:
        self.session.add(row)

    async def rollback(self) -> None:
        await self.session.rollback()

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, row: AiGenerateTaskSourceArchive) -> None:
        await self.session.refresh(row)
