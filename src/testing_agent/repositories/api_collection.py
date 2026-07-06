from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.api_case import ApiCase
from testing_agent.models.api_collection import ApiCollection
from testing_agent.models.project import Project
from testing_agent.models.requirement import Requirement
from testing_agent.models.sprint import Sprint


class ApiCollectionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_requirement(self, requirement_id: str) -> Requirement | None:
        return await self.session.scalar(
            select(Requirement).where(
                Requirement.requirement_id == requirement_id,
                Requirement.deleted_at.is_(None),
            )
        )

    async def get_sprint(self, sprint_id: str) -> Sprint | None:
        return await self.session.scalar(
            select(Sprint).where(Sprint.sprint_id == sprint_id, Sprint.deleted_at.is_(None))
        )

    async def get_project(self, project_id: str) -> Project | None:
        return await self.session.scalar(
            select(Project).where(Project.project_id == project_id, Project.deleted_at.is_(None))
        )

    async def get_collection(self, collection_id: str) -> ApiCollection | None:
        return await self.session.scalar(
            select(ApiCollection).where(
                ApiCollection.collection_id == collection_id,
                ApiCollection.deleted_at.is_(None),
            )
        )

    async def list_by_requirement(self, requirement_id: str) -> list[ApiCollection]:
        return list(
            (
                await self.session.scalars(
                    select(ApiCollection)
                    .where(
                        ApiCollection.requirement_id == requirement_id,
                        ApiCollection.deleted_at.is_(None),
                    )
                    .order_by(ApiCollection.created_at.desc())
                )
            ).all()
        )

    async def exists_case_by_collection_and_name(self, collection_id: str, name: str) -> bool:
        row = await self.session.scalar(
            select(ApiCase.case_id).where(
                ApiCase.collection_id == collection_id,
                ApiCase.name == name,
                ApiCase.deleted_at.is_(None),
            )
        )
        return row is not None

    def add(self, obj: ApiCollection | ApiCase) -> None:
        self.session.add(obj)

    def soft_delete(self, collection: ApiCollection, deleted_at: datetime) -> None:
        collection.deleted_at = deleted_at

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, obj: ApiCollection) -> None:
        await self.session.refresh(obj)

