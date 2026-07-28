from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.project import Project
from testing_agent.models.requirement import Requirement
from testing_agent.models.resource_binding import ResourceBinding
from testing_agent.models.sprint import Sprint


class ResourceBindingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_project(self, project_id: str) -> Project | None:
        return await self.session.scalar(
            select(Project).where(Project.project_id == project_id, Project.deleted_at.is_(None))
        )

    async def get_sprint(self, sprint_id: str) -> Sprint | None:
        return await self.session.scalar(
            select(Sprint).where(Sprint.sprint_id == sprint_id, Sprint.deleted_at.is_(None))
        )

    async def get_requirement(self, requirement_id: str) -> Requirement | None:
        return await self.session.scalar(
            select(Requirement).where(
                Requirement.requirement_id == requirement_id,
                Requirement.deleted_at.is_(None),
            )
        )

    async def get_active_by_local_resource(
        self,
        resource_type: str,
        resource_id: str,
    ) -> ResourceBinding | None:
        return await self.session.scalar(
            select(ResourceBinding)
            .where(
                ResourceBinding.local_resource_type == resource_type,
                ResourceBinding.local_resource_id == resource_id,
                ResourceBinding.status == "active",
                ResourceBinding.deleted_at.is_(None),
            )
            .order_by(ResourceBinding.id.asc())
            .limit(1)
        )

    async def exists_active_by_remote_resource(
        self,
        provider: str,
        connection_id: str,
        remote_resource_type: str,
        remote_resource_id: str,
    ) -> bool:
        row = await self.session.scalar(
            select(ResourceBinding.binding_id)
            .where(
                ResourceBinding.provider == provider,
                ResourceBinding.connection_id == connection_id,
                ResourceBinding.remote_resource_type == remote_resource_type,
                ResourceBinding.remote_resource_id == remote_resource_id,
                ResourceBinding.status == "active",
                ResourceBinding.deleted_at.is_(None),
            )
            .limit(1)
        )
        return row is not None

    async def list(
        self, user_id: str, resource_type: str, resource_id: str
    ) -> list[ResourceBinding]:
        return list(
            (
                await self.session.scalars(
                    select(ResourceBinding)
                    .where(
                        ResourceBinding.user_id == user_id,
                        ResourceBinding.local_resource_type == resource_type,
                        ResourceBinding.local_resource_id == resource_id,
                        ResourceBinding.deleted_at.is_(None),
                    )
                    .order_by(ResourceBinding.created_at.desc())
                )
            ).all()
        )

    async def get(
        self, resource_type: str, resource_id: str, binding_id: str
    ) -> ResourceBinding | None:
        return await self.session.scalar(
            select(ResourceBinding).where(
                ResourceBinding.binding_id == binding_id,
                ResourceBinding.local_resource_type == resource_type,
                ResourceBinding.local_resource_id == resource_id,
                ResourceBinding.deleted_at.is_(None),
            )
        )

    def add(self, binding: ResourceBinding) -> None:
        self.session.add(binding)

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, binding: ResourceBinding) -> None:
        await self.session.refresh(binding)
