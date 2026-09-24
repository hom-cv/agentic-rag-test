"""Larger document passages used as retrieval context."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import child_chunks as child_models
from app.models import documents as document_models
from app.models._base import Base


class ParentChunks(Base):
    __tablename__ = "parent_chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "position", name="uq_parent_chunks_document_position"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source_location: Mapped[str | None] = mapped_column(Text)

    document: Mapped[document_models.Documents] = relationship(
        "Documents", back_populates="parent_chunks", lazy="raise"
    )
    children: Mapped[list[child_models.ChildChunks]] = relationship(
        "ChildChunks", back_populates="parent", cascade="all, delete-orphan",
        passive_deletes=True, order_by="ChildChunks.position", lazy="raise",
    )
