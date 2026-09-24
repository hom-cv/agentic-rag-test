from fastapi import APIRouter, HTTPException
from openai import APIError

from app.schemas.chat import ChatRequest
from app.schemas.retrieval import RetrievalResult
from app.services.retrieval_service import AnnotatedRetrievalService

router = APIRouter(prefix="/retrieval", tags=["Retrieval"])


@router.post("", response_model=list[RetrievalResult])
async def retrieve(
    request: ChatRequest, service: AnnotatedRetrievalService
) -> list[RetrievalResult]:
    """Retrieve matching child passages and parent context for a question."""
    try:
        return await service.retrieve(request)
    except APIError as exc:
        raise HTTPException(
            status_code=502, detail="Could not generate the question embedding"
        ) from exc
