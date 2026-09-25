from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sentence_transformers import CrossEncoder
from starlette.concurrency import run_in_threadpool

from app.schemas.retrieval import RetrievalResult


@lru_cache
def get_model() -> CrossEncoder:
    """Load the reranker"""
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")


class RerankingService:
    async def rerank(
        self, question: str, passages: list[RetrievalResult]
    ) -> list[RetrievalResult]:
        """
        The cross-encoder scores the question and each child's text together.
        RRF scores are not used; they remain unchanged on the returned objects.
        Returns every candidate, best first.
        """
        if not passages:
            return []

        return await run_in_threadpool(self._rerank_passages, question, passages)

    def _rerank_passages(
        self, question: str, passages: list[RetrievalResult]
    ) -> list[RetrievalResult]:
        child_texts = [passage.child_text for passage in passages]
        ranked_matches = get_model().rank(
            question,
            child_texts,
            show_progress_bar=False,
        )

        reranked_passages = []
        for match in ranked_matches:
            # corpus_id is the input list index
            passage_index = match["corpus_id"]

            if not isinstance(passage_index, int):
                raise TypeError("Reranker corpus_id must be an integer")

            reranked_passages.append(passages[passage_index])

        return reranked_passages


AnnotatedRerankingService = Annotated[RerankingService, Depends(RerankingService)]
