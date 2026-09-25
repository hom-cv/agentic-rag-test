from uuid import UUID

from pydantic import BaseModel


class ParentPassage(BaseModel):
    document_id: UUID
    parent_id: UUID
    title: str
    source: str
    source_location: str | None
    content: str


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
    # reciprocal rank fusion score (rrf)
    score: float
