import logging
from typing import Annotated

from fastapi import Depends, HTTPException
from openai import AsyncOpenAI
from openai.types.responses import (
    Response, ResponseInputItemParam, ToolChoiceFunctionParam, ToolChoiceOptions,
)

from app.core.constants import GENERATION_INSTRUCTIONS, GENERATION_OUTPUT_BUDGETS
from app.core.rag_tools import RAG_TOOLS
from app.core.settings import get_settings

logger = logging.getLogger(__name__)


class GenerationService:
    async def generate(
        self,
        messages: list[ResponseInputItemParam],
        tool_choice: ToolChoiceOptions | ToolChoiceFunctionParam,
    ) -> Response:
        """Ask the model for its next retrieval action or final answer."""
        api_key = get_settings().OPENAI_API_KEY
        if not api_key:
            raise HTTPException(status_code=503, detail="No OpenAI API key")

        async with AsyncOpenAI(api_key=api_key, timeout=60.0) as client:
            for output_budget in GENERATION_OUTPUT_BUDGETS:
                response = await client.responses.create(
                    model="gpt-5-nano",
                    instructions=GENERATION_INSTRUCTIONS,
                    input=messages,
                    tools=RAG_TOOLS,
                    tool_choice=tool_choice,
                    parallel_tool_calls=False,
                    reasoning={"effort": "low"},
                    include=["reasoning.encrypted_content"],
                    max_output_tokens=output_budget,
                    store=False,
                )
                if response.status == "completed":
                    return response
                logger.warning(
                    "RAG model status=%s details=%s response_id=%s",
                    response.status, response.incomplete_details, response.id,
                )
                if not (
                    response.incomplete_details
                    and response.incomplete_details.reason == "max_output_tokens"
                ):
                    break

        raise HTTPException(status_code=502, detail="The model did not complete its response")


AnnotatedGenerationService = Annotated[GenerationService, Depends(GenerationService)]
