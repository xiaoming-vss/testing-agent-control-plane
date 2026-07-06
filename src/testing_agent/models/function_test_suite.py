from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from testing_agent.db.base import Base, CreatedAt, IdPk, UpdatedAt
from testing_agent.models.common import SoftDeleteMixin


class FunctionTestSuite(Base, SoftDeleteMixin):
    __tablename__ = "function_test_suites"
    __table_args__ = (
        UniqueConstraint("requirement_id", "name", name="uk_function_suite_requirement_name"),
    )
    id: Mapped[IdPk]
    suite_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    requirement_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
