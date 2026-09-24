from typing import Annotated

from fastapi import Depends

from app.crud.retrieval import AnnotatedRetrievalCRUD
from app.schemas.chat import ChatRequest
from app.schemas.retrieval import RetrievalResult
from app.services.embedding_service import AnnotatedEmbeddingService


class RetrievalService:
    def __init__(
        self, crud: AnnotatedRetrievalCRUD, embedder: AnnotatedEmbeddingService
    ):
        self.crud = crud
        self.embedder = embedder

    async def retrieve(self, request: ChatRequest) -> list[RetrievalResult]:
        """Embed the question and retrieve matching passages with parent context."""
        embedding = await self.embedder.embed(request.question)
        rows = await self.crud.search(embedding, request.limit)

        return [RetrievalResult.model_validate(row) for row in rows]


AnnotatedRetrievalService = Annotated[RetrievalService, Depends(RetrievalService)]
