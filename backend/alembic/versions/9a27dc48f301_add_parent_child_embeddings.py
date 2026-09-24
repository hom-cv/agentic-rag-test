"""Split chunks into parent context and embedded child passages.

Revision ID: 9a27dc48f301
Revises: 0373a41e11e2
"""

import pgvector.sqlalchemy
import sqlalchemy as sa
from alembic import op

revision = "9a27dc48f301"
down_revision = "0373a41e11e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq_documents_source", "documents", ["source"])
    op.add_column("documents", sa.Column("embedding_model", sa.String(100)))
    op.create_table(
        "parent_chunks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("document_id", sa.Uuid(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("source_location", sa.Text()),
        sa.Column("created_date", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_modified_date", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("document_id", "position", name="uq_parent_chunks_document_position"),
    )
    op.create_index("ix_parent_chunks_created_date", "parent_chunks", ["created_date"])
    op.create_table(
        "child_chunks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("parent_id", sa.Uuid(), sa.ForeignKey("parent_chunks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("source_location", sa.Text()),
        sa.Column("embedding", pgvector.sqlalchemy.VECTOR(1536), nullable=False),
        sa.Column("created_date", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_modified_date", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("parent_id", "position", name="uq_child_chunks_parent_position"),
    )
    op.create_index("ix_child_chunks_created_date", "child_chunks", ["created_date"])
    # Preserve any existing flat chunks as one parent and one child each.
    op.execute("""
        INSERT INTO parent_chunks
            (id, document_id, position, text, source_location, created_date, last_modified_date)
        SELECT id, document_id, position, text, source_location, created_date, last_modified_date
        FROM chunks
    """)
    op.execute("""
        INSERT INTO child_chunks
            (id, parent_id, position, text, source_location, embedding, created_date, last_modified_date)
        SELECT id, id, 0, text, source_location, embedding::vector(1536), created_date, last_modified_date
        FROM chunks
    """)
    op.drop_table("chunks")


def downgrade() -> None:
    op.create_table(
        "chunks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("document_id", sa.Uuid(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("source_location", sa.Text()),
        sa.Column("embedding", pgvector.sqlalchemy.VECTOR(), nullable=False),
        sa.Column("created_date", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_modified_date", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("document_id", "position", name="uq_chunks_document_position"),
    )
    op.create_index("ix_chunks_created_date", "chunks", ["created_date"])
    # The old flat schema retains child passages but cannot represent parent context.
    op.execute("""
        INSERT INTO chunks
            (id, document_id, position, text, source_location, embedding, created_date, last_modified_date)
        SELECT c.id, p.document_id,
            row_number() OVER (PARTITION BY p.document_id ORDER BY p.position, c.position) - 1,
            c.text, c.source_location, c.embedding, c.created_date, c.last_modified_date
        FROM child_chunks c JOIN parent_chunks p ON p.id = c.parent_id
    """)
    op.drop_table("child_chunks")
    op.drop_table("parent_chunks")
    op.drop_column("documents", "embedding_model")
    op.drop_constraint("uq_documents_source", "documents", type_="unique")
