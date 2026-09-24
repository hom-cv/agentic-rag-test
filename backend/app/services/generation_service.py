import json
from typing import Annotated

from fastapi import Depends, HTTPException
from openai import AsyncOpenAI

from app.core.constants import GENERATION_INSTRUCTIONS
from app.core.settings import get_settings
from app.schemas.chat import ChatResponse, ChatSource
from app.schemas.retrieval import RetrievalResult


class GenerationService:
    async def generate(
        self, question: str, matches: list[RetrievalResult]
    ) -> ChatResponse:
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

        api_key = get_settings().OPENAI_API_KEY

        if not api_key:
            raise HTTPException(status_code=503, detail="Failed to generate, no OpenAI API key")

        async with AsyncOpenAI(api_key=api_key, timeout=60.0) as client:
            response = await client.responses.create(
                model="gpt-5-nano",
                instructions=GENERATION_INSTRUCTIONS,
                input=json.dumps({"question": question, "sources": context}),
                reasoning={"effort": "low"},
                max_output_tokens=4096,
                store=False,
            )

        if response.status != "completed" or not response.output_text.strip():
            raise HTTPException(status_code=502, detail="The model did not return a complete answer")

        return ChatResponse(answer=response.output_text, sources=sources)


AnnotatedGenerationService = Annotated[GenerationService, Depends(GenerationService)]
