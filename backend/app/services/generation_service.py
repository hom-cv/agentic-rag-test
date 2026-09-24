from typing import Annotated

from fastapi import Depends, HTTPException
from openai import AsyncOpenAI

from app.core.constants import GENERATION_INSTRUCTIONS
from app.core.settings import get_settings


class GenerationService:
    async def generate(self, prompt: str) -> str:
        """Generate an answer from a prepared prompt."""
        api_key = get_settings().OPENAI_API_KEY

        if not api_key:
            raise HTTPException(status_code=503, detail="Failed to generate, no OpenAI API key")

        async with AsyncOpenAI(api_key=api_key, timeout=60.0) as client:
            response = await client.responses.create(
                model="gpt-5-nano",
                instructions=GENERATION_INSTRUCTIONS,
                input=prompt,
                reasoning={"effort": "low"},
                max_output_tokens=4096,
                store=False,
            )

        if response.status != "completed" or not response.output_text.strip():
            raise HTTPException(status_code=502, detail="The model did not return a complete answer")

        return response.output_text


AnnotatedGenerationService = Annotated[GenerationService, Depends(GenerationService)]
