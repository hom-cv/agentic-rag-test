import json
from typing import Annotated

from fastapi import Depends

from app.schemas.chat import ChatRequest, ChatResponse, ChatSource
from app.services.embedding_service import AnnotatedEmbeddingService
from app.services.generation_service import AnnotatedGenerationService
from app.services.retrieval_service import AnnotatedRetrievalService


class ChatService:
    def __init__(
        self,
        embedder: AnnotatedEmbeddingService,
        retrieval: AnnotatedRetrievalService,
        generation: AnnotatedGenerationService,
    ):
        self.embedder = embedder
        self.retrieval = retrieval
        self.generation = generation

    async def generate_rag_response(self, request: ChatRequest) -> ChatResponse:
        """Retrieve passages, prepare parent context, and generate an answer."""
        embedding = await self.embedder.embed(request.question)
        matches = await self.retrieval.retrieve(embedding, request.limit)

        if not matches:
            return ChatResponse(
                answer="I couldn't find any document passages to answer this question.",
                sources=[],
            )

        sources = []
        context = []
        seen_parents = set()

        for match in matches:
            if match.parent_id in seen_parents:
                continue

            seen_parents.add(match.parent_id)
            source = ChatSource(
                label=f"S{len(sources) + 1}",
                document_id=match.document_id,
                parent_id=match.parent_id,
                title=match.title,
                source=match.source,
                source_location=match.parent_source_location,
            )
            sources.append(source)
            context.append({
                **source.model_dump(mode="json"),
                "content": match.parent_text,
            })

        prompt = json.dumps({"question": request.question, "sources": context})
        answer = await self.generation.generate(prompt)

        return ChatResponse(answer=answer, sources=sources)


AnnotatedChatService = Annotated[ChatService, Depends(ChatService)]
