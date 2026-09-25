from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import RowMapping, Select, func, literal_column, select

from app.api.dependencies.db import AnnotatedSession
from app.models import ChildChunks, Documents, ParentChunks


class RetrievalCRUD:
    def __init__(self, session: AnnotatedSession):
        self.session = session

    def _candidates(self) -> Select:
        return (
            select(ChildChunks.id)
            .join(ParentChunks, ChildChunks.parent_id == ParentChunks.id)
            .join(Documents, ParentChunks.document_id == Documents.id)
            .where(
                Documents.ingestion_status == "completed",
                Documents.embedding_model == "text-embedding-3-small",
            )
        )

    async def vector_search(self, embedding: list[float], limit: int) -> list[UUID]:
        # set HNSW search depth for this transaction to cover the candidate limit.
        await self.session.execute(
            select(func.set_config("hnsw.ef_search", str(max(40, limit)), True))
        )

        statement = self._candidates().order_by(
            ChildChunks.embedding.cosine_distance(embedding)
        ).limit(limit)

        result = await self.session.scalars(statement)

        return list(result)

    async def keyword_search(self, question: str, limit: int) -> list[UUID]:
        # standard full text search implementation
        # use English search rules (english::regconfig)
        config = literal_column("'english'::regconfig")
        # turn chunk text into searchable words.
        document = func.to_tsvector(config, ChildChunks.text)
        # turn the question into a search query.
        query = func.websearch_to_tsquery(config, question)

        # get the top matching chunks.
        statement = (
            self._candidates()
            .where(document.bool_op("@@")(query))
            .order_by(func.ts_rank_cd(document, query).desc(), ChildChunks.id)
            .limit(limit)
        )

        result = await self.session.scalars(statement)

        return list(result)

    async def get_chunks(self, child_ids: list[UUID]) -> list[RowMapping]:
        statement = (
            select(
                Documents.id.label("document_id"),
                Documents.title,
                Documents.source,
                ParentChunks.id.label("parent_id"),
                ChildChunks.id.label("child_id"),
                ChildChunks.text.label("child_text"),
                ParentChunks.text.label("parent_text"),
                ChildChunks.source_location.label("child_source_location"),
                ParentChunks.source_location.label("parent_source_location"),
            )
            .select_from(ChildChunks)
            .join(ParentChunks, ChildChunks.parent_id == ParentChunks.id)
            .join(Documents, ParentChunks.document_id == Documents.id)
            .where(ChildChunks.id.in_(child_ids))
        )
        result = await self.session.execute(statement)
        return list(result.mappings())


AnnotatedRetrievalCRUD = Annotated[RetrievalCRUD, Depends(RetrievalCRUD)]
