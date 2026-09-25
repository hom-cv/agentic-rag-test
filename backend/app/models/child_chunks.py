"""Small passages with embeddings for similarity search."""

from __future__ import annotations

import uuid

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy import text as sql_text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import parent_chunks as parent_models
from app.models._base import Base


class ChildChunks(Base):
    __tablename__ = "child_chunks"
    __table_args__ = (
        UniqueConstraint("parent_id", "position", name="uq_child_chunks_parent_position"),
        # HNSW uses graphs for fast approximate nearest-neighbor search.
        # postgresql_ops tells the index to compare embeddings using cosine.
        Index(
            "ix_child_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        # indexing on child chunk texts for faster keyword search
        Index(
            "ix_child_chunks_text_fts",
            sql_text("to_tsvector('english'::regconfig, text)"),
            postgresql_using="gin",
        ),
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
