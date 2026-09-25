from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


class SearchDocumentsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
    limit: Annotated[int, Field(ge=1, le=100)]


class GetParentChunkInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parent_id: UUID
