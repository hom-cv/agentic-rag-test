from typing import Annotated

from fastapi import Depends

from app.crud.retrieval import AnnotatedRetrievalCRUD
from app.schemas.retrieval import RetrievalResult


class RetrievalService:
    def __init__(self, crud: AnnotatedRetrievalCRUD):
        self.crud = crud

    async def retrieve(
        self, embedding: list[float], limit: int
    ) -> list[RetrievalResult]:
        """Retrieve matching passages and parent context for a query embedding."""
        rows = await self.crud.search(embedding, limit)

        return [RetrievalResult.model_validate(row) for row in rows]


AnnotatedRetrievalService = Annotated[RetrievalService, Depends(RetrievalService)]
