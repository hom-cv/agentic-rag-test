from uuid import UUID, uuid4

from pydantic import BaseModel, Field, PositiveInt


class ChildChunk(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    parent_id: UUID
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
