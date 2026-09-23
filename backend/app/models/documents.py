"""Document model"""

from __future__ import annotations

import uuid

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import chunks as chunks_models
from app.models._base import Base


class Documents(Base):
    """Source metadata and ingestion state for a document."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    source: Mapped[str] = mapped_column(Text, nullable=False)
    ingestion_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
    )

    chunks: Mapped[list[chunks_models.Chunks]] = relationship(
        "Chunks",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Chunks.position",
        lazy="raise",
    )
