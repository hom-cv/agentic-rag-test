import json
from uuid import UUID, uuid4

from core.db import get_session_factory
from models import ChildChunks, Documents, ParentChunks
from schemas.transform import TransformedDocument
from sqlalchemy import delete, func
from sqlalchemy.dialects.postgresql import insert


class LoadService:
    def load_document(self, document: TransformedDocument) -> UUID:
        """Replace a source document's chunks in one transaction."""

        if document.embedding_model != "text-embedding-3-small" or document.embedding_dimensions != 1536:
            raise ValueError("Run transform to generate text-embedding-3-small embeddings first")

        if not document.parents:
            raise ValueError(f"No chunks to load for {document.source}")

        for parent in document.parents:
            for child in parent.children:
                if child.parent_id != parent.id or child.embedding is None:
                    raise ValueError(f"Child {child.id} needs a matching parent and embedding")

        session_factory = get_session_factory()

        with session_factory.begin() as session:
            statement = insert(Documents).values(
                id=uuid4(),
                title=document.title,
                source=document.source,
                ingestion_status="completed",
                embedding_model=document.embedding_model,
            )

            statement = statement.on_conflict_do_update(
                index_elements=[Documents.source],
                set_={
                    "title": statement.excluded.title,
                    "ingestion_status": "completed",
                    "embedding_model": statement.excluded.embedding_model,
                    "last_modified_date": func.now(),
                },
            ).returning(Documents.id)

            document_id = session.execute(statement).scalar_one()

            session.execute(
                delete(ParentChunks).where(ParentChunks.document_id == document_id)
            )

            for position, parent in enumerate(document.parents):
                session.add(ParentChunks(
                    id=parent.id,
                    document_id=document_id,
                    position=position,
                    text_=parent.content,
                    source_location=json.dumps(parent.pages),
                ))

            session.flush()

            for parent in document.parents:
                for position, child in enumerate(parent.children):
                    session.add(ChildChunks(
                        id=child.id,
                        parent_id=parent.id,
                        position=position,
                        text_=child.content,
                        source_location=json.dumps(child.pages),
                        embedding=child.embedding,
                    ))

        return document_id
