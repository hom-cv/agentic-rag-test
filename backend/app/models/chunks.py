"""Retrievable document chunks and their embeddings."""

from __future__ import annotations

import uuid

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import documents as document_models
from app.models._base import Base


class Chunks(Base):
    """A zero-based, ordered text segment belonging to one document."""

    __tablename__ = "chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "position", name="uq_chunks_document_position"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source_location: Mapped[str | None] = mapped_column(Text)

    embedding: Mapped[list[float]] = mapped_column(VECTOR(), nullable=False)

    # document relationship with chunks
    document: Mapped[document_models.Documents] = relationship(
        "Documents", back_populates="chunks", lazy="raise"
    )
