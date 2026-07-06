from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from testing_agent.db.base import Base, CreatedAt, IdPk, UpdatedAt
from testing_agent.models.common import SoftDeleteMixin


class Project(Base, SoftDeleteMixin):
    __tablename__ = "projects"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uk_project_user_name"),)
    id: Mapped[IdPk]
    project_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    source_type: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    binding_status: Mapped[str] = mapped_column(
        String(20), index=True, nullable=False, default="unbound"
    )
    last_bound_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_binding_sync_error: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
