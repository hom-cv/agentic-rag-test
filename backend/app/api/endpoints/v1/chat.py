from fastapi import APIRouter, HTTPException
from openai import APIError

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import AnnotatedChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: AnnotatedChatService,
) -> ChatResponse:
    """Answer one question using retrieved document context."""
    try:
        return await service.generate_rag_response(request)
    except APIError as exc:
        raise HTTPException(
            status_code=502, detail="Could not complete the model request"
        ) from exc
