from fastapi import APIRouter

from app.api.endpoints.v1.chat import router as chat_router
from app.api.endpoints.v1.retrieval import router as retrieval_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(retrieval_router)
api_router.include_router(chat_router)
