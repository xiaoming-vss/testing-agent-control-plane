from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from testing_agent.db.base import Base, CreatedAt, IdPk, UpdatedAt
from testing_agent.models.common import SoftDeleteMixin


class ApiCollection(Base, SoftDeleteMixin):
    __tablename__ = "api_collections"
    __table_args__ = (
        UniqueConstraint("requirement_id", "name", name="uk_api_collection_requirement_name"),
    )
    id: Mapped[IdPk]
    collection_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    requirement_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
