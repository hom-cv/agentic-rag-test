from fastapi import APIRouter, HTTPException
from openai import APIError

from app.schemas.chat import ChatRequest
from app.schemas.retrieval import RetrievalResult
from app.services.embedding_service import AnnotatedEmbeddingService
from app.services.retrieval_service import AnnotatedRetrievalService

router = APIRouter(prefix="/retrieval", tags=["Retrieval"])


@router.post("", response_model=list[RetrievalResult])
async def retrieve(
    request: ChatRequest,
    embedder: AnnotatedEmbeddingService,
    service: AnnotatedRetrievalService,
) -> list[RetrievalResult]:
    """Retrieve matching child passages and parent context for a question."""
    try:
        embedding = await embedder.embed(request.question)

        return await service.retrieve(embedding, request.limit)
    except APIError as exc:
        raise HTTPException(
            status_code=502, detail="Could not generate the question embedding"
        ) from exc
