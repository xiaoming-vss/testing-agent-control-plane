from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.api_extract_rule import ApiExtractRule


class ApiExtractRuleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_rule(self, extract_rule_id: str) -> ApiExtractRule | None:
        return await self.session.scalar(
            select(ApiExtractRule).where(
                ApiExtractRule.extract_rule_id == extract_rule_id,
                ApiExtractRule.deleted_at.is_(None),
            )
        )

    async def list_by_case(self, case_id: str) -> list[ApiExtractRule]:
        return list(
            (
                await self.session.scalars(
                    select(ApiExtractRule)
                    .where(
                        ApiExtractRule.case_id == case_id,
                        ApiExtractRule.deleted_at.is_(None),
                    )
                    .order_by(ApiExtractRule.order_no)
                )
            ).all()
        )

    def add(self, rule: ApiExtractRule) -> None:
        self.session.add(rule)

    def soft_delete(self, rule: ApiExtractRule, deleted_at: datetime) -> None:
        rule.deleted_at = deleted_at

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, rule: ApiExtractRule) -> None:
        await self.session.refresh(rule)

