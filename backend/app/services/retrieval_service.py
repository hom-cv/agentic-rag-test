from typing import Annotated

from fastapi import Depends

from app.crud.retrieval import AnnotatedRetrievalCRUD
from app.schemas.retrieval import RetrievalResult
from app.utils.rrf import reciprocal_rank_fusion


class RetrievalService:
    def __init__(self, crud: AnnotatedRetrievalCRUD):
        self.crud = crud

    async def retrieve(
        self, question: str, embedding: list[float], limit: int
    ) -> list[RetrievalResult]:
        """
        Fetch children ranked by cosine similarity and by keyword search,
        then using their respective ranks from each retrieval method,
        calculates the rrf to rank the documents.
        """
        candidate_limit = max(20, limit * 4)
        vector_ids = await self.crud.vector_search(embedding, candidate_limit)
        keyword_ids = await self.crud.keyword_search(question, candidate_limit)

        ranked = reciprocal_rank_fusion([vector_ids, keyword_ids], limit)
        selected = [child_id for child_id, _ in ranked]
        scores = dict(ranked)

        if not selected:
            return []

        rows = await self.crud.get_chunks(selected)
        results = {
            row["child_id"]: RetrievalResult.model_validate({
                **row, "score": scores[row["child_id"]],
            })
            for row in rows
        }

        return [results[child_id] for child_id in selected if child_id in results]


AnnotatedRetrievalService = Annotated[RetrievalService, Depends(RetrievalService)]
