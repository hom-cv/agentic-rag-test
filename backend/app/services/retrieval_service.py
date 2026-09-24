from typing import Annotated

from fastapi import Depends

from app.crud.retrieval import AnnotatedRetrievalCRUD
from app.schemas.retrieval import RetrievalQuery, RetrievalResult


class RetrievalService:
    def __init__(self, crud: AnnotatedRetrievalCRUD):
        self.crud = crud

    async def search(self, query: RetrievalQuery) -> list[RetrievalResult]:
        """Return matching child passages with their parent context."""
        rows = await self.crud.search(query.embedding, query.limit)

        return [RetrievalResult.model_validate(row) for row in rows]


AnnotatedRetrievalService = Annotated[RetrievalService, Depends(RetrievalService)]
