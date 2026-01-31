from datetime import datetime, timezone
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import object_session
import sqlalchemy as sa

from app import db
from app.models.document import Document


class DocumentEmbedding(db.Model):
    __tablename__ = "document_embeddings"
    _UTCNOW = staticmethod(lambda: datetime.now(timezone.utc))

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    document_id = db.Column(
        db.String(36), db.ForeignKey("documents.id"), nullable=False, index=True
    )
    document_type = db.Column(db.String(255), nullable=True, index=True)
    embedding = db.Column(Vector(), nullable=False)
    chunk_index = db.Column(db.Integer, nullable=False, default=0)
    content = db.Column(db.Text, nullable=True)
    metadata_ = db.Column("metadata", JSONB, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_UTCNOW)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=_UTCNOW,
        onupdate=_UTCNOW,
    )

    document = db.relationship(
        "Document", backref=db.backref("embeddings", lazy="dynamic")
    )

    __table_args__ = (
        db.UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_embeddings_document_chunk",
        ),
    )


def _load_document_type(target):
    if target.document is not None:
        return target.document.document_type

    session = object_session(target)
    if session is None or target.document_id is None:
        return target.document_type

    document = session.get(Document, target.document_id)
    if document is None:
        return target.document_type

    return document.document_type


@event.listens_for(DocumentEmbedding, "before_insert")
@event.listens_for(DocumentEmbedding, "before_update")
def _sync_document_type(mapper, connection, target):
    target.document_type = _load_document_type(target)


@event.listens_for(Document, "after_update")
def _propagate_document_type(mapper, connection, target):
    connection.execute(
        sa.text(
            "UPDATE document_embeddings "
            "SET document_type = :document_type "
            "WHERE document_id = :document_id"
        ),
        {"document_type": target.document_type, "document_id": target.id},
    )
