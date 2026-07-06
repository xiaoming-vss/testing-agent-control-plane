from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, String, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from testing_agent.db.base import Base, CreatedAt, IdPk, UpdatedAt
from testing_agent.models.common import SoftDeleteMixin


class Requirement(Base, SoftDeleteMixin):
    __tablename__ = "requirements"
    __table_args__ = (UniqueConstraint("sprint_id", "name", name="uk_requirement_sprint_name"),)
    id: Mapped[IdPk]
    requirement_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    sprint_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    document_type: Mapped[str] = mapped_column(String(20), nullable=False, default="text")
    document_content: Mapped[str] = mapped_column(LONGTEXT, nullable=False, default="")
    document_filename: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    document_hash: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    document_storage_path: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    document_download_url: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    source_type: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    binding_status: Mapped[str] = mapped_column(
        String(20), index=True, nullable=False, default="unbound"
    )
    last_bound_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_binding_sync_error: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
