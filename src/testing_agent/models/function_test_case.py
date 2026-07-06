from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from testing_agent.db.base import Base, CreatedAt, IdPk, UpdatedAt
from testing_agent.models.common import SoftDeleteMixin


class FunctionTestCase(Base, SoftDeleteMixin):
    __tablename__ = "function_test_cases"
    __table_args__ = (
        UniqueConstraint("suite_id", "title", name="uk_function_case_suite_title"),
        Index("idx_function_case_suite_order", "suite_id", "order_no"),
    )
    id: Mapped[IdPk]
    case_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    suite_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    module: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    preconditions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    steps: Mapped[str] = mapped_column(LONGTEXT, nullable=False, default="")
    expected_results: Mapped[str] = mapped_column(LONGTEXT, nullable=False, default="")
    priority: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    case_type: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    order_no: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
