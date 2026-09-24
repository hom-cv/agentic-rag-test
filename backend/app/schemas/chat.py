from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints


class ChatRequest(BaseModel):
    question: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)
    ]
    limit: Annotated[int, Field(gt=0, le=100)] = 5


class ChatSource(BaseModel):
    label: str
    document_id: UUID
    parent_id: UUID
    title: str
    source: str
    source_location: str | None


class ChatResponse(BaseModel):
    answer: str
    # All passages supplied as context, including any the answer does not cite.
    sources: list[ChatSource]
