from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, FiniteFloat, PositiveInt


class ChildChunk(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    parent_id: UUID
    embedding: list[FiniteFloat] | None = Field(default=None, min_length=1536, max_length=1536)
    content: str
    pages: list[PositiveInt]


class ParentChunk(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    content: str
    pages: list[PositiveInt]
    children: list[ChildChunk] = Field(default_factory=list)


class TransformedDocument(BaseModel):
    title: str
    source: str
    parents: list[ParentChunk]
    embedding_model: Literal["text-embedding-3-small"] | None = None
    embedding_dimensions: Literal[1536] | None = None
