from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, FiniteFloat, field_validator


class RetrievalQuery(BaseModel):
    """A text-embedding-3-small vector and the number of child matches to fetch."""

    embedding: Annotated[
        list[FiniteFloat], Field(min_length=1536, max_length=1536)
    ]
    limit: Annotated[int, Field(gt=0)] = 5

    @field_validator("embedding")
    @classmethod
    def validate_nonzero_embedding(cls, embedding: list[float]) -> list[float]:
        if not any(embedding):
            raise ValueError("Cosine search requires a nonzero embedding")

        return embedding


class RetrievalResult(BaseModel):
    document_id: UUID
    title: str
    source: str
    parent_id: UUID
    child_id: UUID
    child_text: str
    parent_text: str
    child_source_location: str | None
    parent_source_location: str | None
    score: float
