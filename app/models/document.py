from datetime import datetime, timezone
from uuid import uuid4

from app import db


class Document(db.Model):
    __tablename__ = "documents"
    _UTCNOW = staticmethod(lambda: datetime.now(timezone.utc))

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    document_type = db.Column(db.String(255), nullable=True)
    original_filename = db.Column(db.String(255), nullable=False)
    storage_key = db.Column(db.String(1024), nullable=False)
    storage_provider = db.Column(db.String(50), nullable=False, default="s3")
    content_type = db.Column(db.String(255), nullable=True)
    size_bytes = db.Column(db.BigInteger, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_UTCNOW)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=_UTCNOW,
        onupdate=_UTCNOW,
    )
