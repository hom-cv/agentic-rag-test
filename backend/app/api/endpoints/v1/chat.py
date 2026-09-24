from fastapi import APIRouter, HTTPException
from openai import APIError

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.generation_service import AnnotatedGenerationService
from app.services.retrieval_service import AnnotatedRetrievalService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    retrieval: AnnotatedRetrievalService,
    generation: AnnotatedGenerationService,
) -> ChatResponse:
    """Answer one question using retrieved document context."""
    try:
        matches = await retrieval.retrieve(request)

        return await generation.generate(request.question, matches)
    except APIError as exc:
        raise HTTPException(
            status_code=502, detail="Could not complete the model request"
        ) from exc
