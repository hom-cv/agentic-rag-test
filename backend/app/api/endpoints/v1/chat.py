from fastapi import APIRouter, HTTPException
from openai import APIError

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import AnnotatedRAGService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: AnnotatedRAGService,
) -> ChatResponse:
    """Answer one question using retrieved document context."""
    try:
        return await service.chat(request)
    except APIError as exc:
        raise HTTPException(
            status_code=502, detail="Could not complete the model request"
        ) from exc
