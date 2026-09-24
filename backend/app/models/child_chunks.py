"""Small passages with embeddings for similarity search."""

from __future__ import annotations

import uuid

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import parent_chunks as parent_models
from app.models._base import Base


class ChildChunks(Base):
    __tablename__ = "child_chunks"
    __table_args__ = (
        UniqueConstraint("parent_id", "position", name="uq_child_chunks_parent_position"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    parent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("parent_chunks.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source_location: Mapped[str | None] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(VECTOR(1536), nullable=False)

    parent: Mapped[parent_models.ParentChunks] = relationship(
        "ParentChunks", back_populates="children", lazy="raise"
    )
