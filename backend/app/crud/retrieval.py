from typing import Annotated

from fastapi import Depends
from sqlalchemy import RowMapping, select

from app.api.dependencies.db import AnnotatedSession
from app.models import ChildChunks, Documents, ParentChunks


class RetrievalCRUD:
    def __init__(self, session: AnnotatedSession):
        self.session = session

    async def search(self, embedding: list[float], limit: int) -> list[RowMapping]:
        """Find the closest child passages and include their parent context.

        Results are ranked by cosine similarity, highest first. Multiple child
        matches may share a parent; the limit counts children, not unique parents.
        """
        distance = ChildChunks.embedding.cosine_distance(embedding)

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
                (1 - distance).label("score"),
            )
            .select_from(ChildChunks)
            .join(ParentChunks, ChildChunks.parent_id == ParentChunks.id)
            .join(Documents, ParentChunks.document_id == Documents.id)
            .where(
                Documents.ingestion_status == "completed",
                Documents.embedding_model == "text-embedding-3-small",
            )
            .order_by(distance)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return list(result.mappings())


AnnotatedRetrievalCRUD = Annotated[RetrievalCRUD, Depends(RetrievalCRUD)]
