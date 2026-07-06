from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from testing_agent.models.api_assert_rule import ApiAssertRule


class ApiAssertRuleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_rule(self, assert_rule_id: str) -> ApiAssertRule | None:
        return await self.session.scalar(
            select(ApiAssertRule).where(
                ApiAssertRule.assert_rule_id == assert_rule_id,
                ApiAssertRule.deleted_at.is_(None),
            )
        )

    async def list_by_case(self, case_id: str) -> list[ApiAssertRule]:
        return list(
            (
                await self.session.scalars(
                    select(ApiAssertRule)
                    .where(
                        ApiAssertRule.case_id == case_id,
                        ApiAssertRule.deleted_at.is_(None),
                    )
                    .order_by(ApiAssertRule.order_no)
                )
            ).all()
        )

    def add(self, rule: ApiAssertRule) -> None:
        self.session.add(rule)

    def soft_delete(self, rule: ApiAssertRule, deleted_at: datetime) -> None:
        rule.deleted_at = deleted_at

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, rule: ApiAssertRule) -> None:
        await self.session.refresh(rule)

