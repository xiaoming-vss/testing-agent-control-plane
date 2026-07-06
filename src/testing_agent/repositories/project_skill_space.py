from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.project import Project
from testing_agent.models.project_skill_space import ProjectSkillSpace


class ProjectSkillSpaceRepository:
    writes_files = True

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_project(self, project_id: str) -> Project | None:
        return await self.session.scalar(
            select(Project).where(Project.project_id == project_id, Project.deleted_at.is_(None))
        )

    async def list(self, project_id: str) -> list[ProjectSkillSpace]:
        return list(
            (
                await self.session.scalars(
                    select(ProjectSkillSpace)
                    .where(
                        ProjectSkillSpace.project_id == project_id,
                        ProjectSkillSpace.deleted_at.is_(None),
                    )
                    .order_by(ProjectSkillSpace.created_at.desc())
                )
            ).all()
        )

    async def get(self, project_id: str, skill_space_id: str) -> ProjectSkillSpace | None:
        return await self.session.scalar(
            select(ProjectSkillSpace).where(
                ProjectSkillSpace.project_id == project_id,
                ProjectSkillSpace.skill_space_id == skill_space_id,
                ProjectSkillSpace.deleted_at.is_(None),
            )
        )

    async def get_by_project_and_filename_unscoped(
        self, project_id: str, filename: str
    ) -> ProjectSkillSpace | None:
        return await self.session.scalar(
            select(ProjectSkillSpace).where(
                ProjectSkillSpace.project_id == project_id,
                ProjectSkillSpace.filename == filename,
            )
        )

    def restore(self, skill: ProjectSkillSpace) -> None:
        skill.deleted_at = None
        self.session.add(skill)

    def add(self, skill: ProjectSkillSpace) -> None:
        self.session.add(skill)

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, skill: ProjectSkillSpace) -> None:
        await self.session.refresh(skill)
