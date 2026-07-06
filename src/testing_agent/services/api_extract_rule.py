from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from testing_agent.core.errors import ErrNotFound
from testing_agent.core.sid import new_id
from testing_agent.models.api_extract_rule import ApiExtractRule
from testing_agent.repositories.api_extract_rule import ApiExtractRuleRepository
from testing_agent.schemas.api_extract_rule import ApiExtractRuleRequest, ApiExtractRuleResponse
from testing_agent.services.api_case import ApiCaseService
from testing_agent.services.common import apply_patch, dump


class ApiExtractRuleService:
    def __init__(self, repository: ApiExtractRuleRepository, api_cases: ApiCaseService):
        self.repository = repository
        self.api_cases = api_cases

    async def get_owned_entity(self, user_id: str, extract_rule_id: str) -> ApiExtractRule:
        rule = await self.repository.get_rule(extract_rule_id)
        if rule is None:
            raise ErrNotFound
        await self.api_cases.get_owned_context(user_id, rule.case_id)
        return rule

    async def create(self, user_id: str, case_id: str, body: ApiExtractRuleRequest) -> dict:
        await self.api_cases.get_owned_context(user_id, case_id)
        rule = ApiExtractRule(extract_rule_id=new_id(), case_id=case_id, **body.model_dump())
        self.repository.add(rule)
        await self.repository.commit()
        await self.repository.refresh(rule)
        return dump(ApiExtractRuleResponse, rule)

    async def list(self, user_id: str, case_id: str) -> list[dict]:
        await self.api_cases.get_owned_context(user_id, case_id)
        rows = await self.repository.list_by_case(case_id)
        return [dump(ApiExtractRuleResponse, row) for row in rows]

    async def get(self, user_id: str, extract_rule_id: str) -> dict:
        return dump(ApiExtractRuleResponse, await self.get_owned_entity(user_id, extract_rule_id))

    async def update(self, user_id: str, extract_rule_id: str, body: dict[str, Any]) -> dict:
        rule = await self.get_owned_entity(user_id, extract_rule_id)
        apply_patch(
            rule,
            body,
            {
                "name",
                "enabled",
                "order_no",
                "source",
                "source_expr",
                "var_key",
                "default_value",
            },
        )
        await self.repository.commit()
        await self.repository.refresh(rule)
        return dump(ApiExtractRuleResponse, rule)

    async def delete(self, user_id: str, extract_rule_id: str) -> dict:
        rule = await self.get_owned_entity(user_id, extract_rule_id)
        self.repository.soft_delete(rule, datetime.now(UTC))
        await self.repository.commit()
        return {}
