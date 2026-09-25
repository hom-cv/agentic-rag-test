import json
import re
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from openai.types.responses import (
    ResponseFunctionToolCall, ResponseInputItemParam,
    ToolChoiceFunctionParam, ToolChoiceOptions,
)
from pydantic import ValidationError

from app.core.constants import MAX_RETRIEVAL_ROUNDS
from app.schemas.agent import GetParentChunkInput, SearchDocumentsInput
from app.schemas.chat import ChatRequest, ChatResponse, ChatSource
from app.services.embedding_service import AnnotatedEmbeddingService
from app.services.generation_service import AnnotatedGenerationService
from app.services.reranking_service import AnnotatedRerankingService
from app.services.retrieval_service import AnnotatedRetrievalService


class ChatService:
    def __init__(
        self,
        embedder: AnnotatedEmbeddingService,
        retrieval: AnnotatedRetrievalService,
        generation: AnnotatedGenerationService,
        reranker: AnnotatedRerankingService,
    ):
        self.embedder = embedder
        self.retrieval = retrieval
        self.generation = generation
        self.reranker = reranker

    async def generate_rag_response(self, request: ChatRequest) -> ChatResponse:
        """Let the model retrieve evidence, then answer within a fixed tool budget."""
        messages: list[ResponseInputItemParam] = [{
            "role": "user",
            "content": json.dumps({"question": request.question, "initial_limit": request.limit}),
        }]
        sources: dict[UUID, ChatSource] = {}
        previous_calls: set[tuple[str, str]] = set()

        for round_number in range(MAX_RETRIEVAL_ROUNDS + 1):
            tool_choice: ToolChoiceOptions | ToolChoiceFunctionParam = "auto"
            if round_number == 0:
                tool_choice = {"type": "function", "name": "search_documents"}
            elif round_number == MAX_RETRIEVAL_ROUNDS:
                tool_choice = "none"

            response = await self.generation.generate(messages, tool_choice)
            calls = [item for item in response.output if item.type == "function_call"]
            if not calls:
                answer = response.output_text.strip()
                if not answer or round_number == 0:
                    raise HTTPException(status_code=502, detail="The model did not answer from retrieved evidence")
                labels = {source.label for source in sources.values()}
                if not set(re.findall(r"\bS\d+\b", answer)).issubset(labels):
                    raise HTTPException(status_code=502, detail="The model cited an unknown source")
                return ChatResponse(answer=answer, sources=list(sources.values()))

            if len(calls) != 1 or round_number == MAX_RETRIEVAL_ROUNDS:
                raise HTTPException(status_code=502, detail="The model exceeded its retrieval budget")

            # Replay tool calls and reasoning items for the next model turn.
            messages.extend(item.model_dump(mode="json", exclude_none=True) for item in response.output)
            call = calls[0]
            try:
                call_key = (call.name, json.dumps(json.loads(call.arguments), sort_keys=True))
                if call_key in previous_calls:
                    output = {"error": "This call was already made. Use the existing evidence or try a different call."}
                else:
                    previous_calls.add(call_key)
                    output = await self._run_tool(
                        call, sources, request.limit if round_number == 0 else None
                    )
            except (ValidationError, json.JSONDecodeError):
                output = {"error": "Invalid tool arguments. Follow the tool schema."}
            messages.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps({
                    "result": output,
                    "remaining_retrieval_calls": MAX_RETRIEVAL_ROUNDS - round_number - 1,
                }),
            })

        raise HTTPException(status_code=502, detail="The model did not return an answer")

    async def _run_tool(
        self,
        call: ResponseFunctionToolCall,
        sources: dict[UUID, ChatSource],
        initial_limit: int | None,
    ) -> dict:
        if call.name == "search_documents":
            args = SearchDocumentsInput.model_validate_json(call.arguments)
            limit = initial_limit if initial_limit is not None else args.limit
            embedding = await self.embedder.embed(args.query)
            candidates = await self.retrieval.retrieve(args.query, embedding, max(20, limit * 4))
            matches = await self.reranker.rerank(args.query, candidates)
            passages = []
            seen_parents: set[UUID] = set()
            for match in matches[:limit]:
                if match.parent_id in seen_parents:
                    continue
                seen_parents.add(match.parent_id)
                if match.parent_id not in sources:
                    sources[match.parent_id] = ChatSource(
                        label=f"S{len(sources) + 1}",
                        document_id=match.document_id,
                        parent_id=match.parent_id,
                        title=match.title,
                        source=match.source,
                        source_location=match.parent_source_location,
                    )
                passages.append({
                    **sources[match.parent_id].model_dump(mode="json"),
                    "content": match.parent_text,
                })
            return {"passages": passages, "limit": limit}

        if call.name == "get_parent_chunk":
            args = GetParentChunkInput.model_validate_json(call.arguments)
            if args.parent_id not in sources:
                return {"error": "Use a parent_id returned by search_documents."}
            passage = await self.retrieval.get_parent_chunk(args.parent_id)
            if passage is None:
                return {"error": "The parent passage is no longer available."}
            return {
                "label": sources[args.parent_id].label,
                **passage.model_dump(mode="json"),
            }

        return {"error": "Unknown tool. Use search_documents or get_parent_chunk."}


AnnotatedChatService = Annotated[ChatService, Depends(ChatService)]
