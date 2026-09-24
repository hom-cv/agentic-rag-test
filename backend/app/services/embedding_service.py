from typing import Annotated

from fastapi import Depends, HTTPException
from openai import AsyncOpenAI

from app.core.settings import get_settings


class EmbeddingService:
    async def embed(self, text: str) -> list[float]:
        api_key = get_settings().OPENAI_API_KEY

        if not api_key:
            raise HTTPException(status_code=503, detail="Failed to embed, No OpenAI API key")

        async with AsyncOpenAI(api_key=api_key, timeout=30.0) as client:
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                dimensions=1536,
                encoding_format="float",
            )

        return response.data[0].embedding


AnnotatedEmbeddingService = Annotated[EmbeddingService, Depends(EmbeddingService)]
