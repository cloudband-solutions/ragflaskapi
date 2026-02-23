from datetime import datetime, timezone
from uuid import uuid4

from app import db


class User(db.Model):
    __tablename__ = "users"
    _UTCNOW = staticmethod(lambda: datetime.now(timezone.utc))

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="pending")
    user_type = db.Column(db.String(50), nullable=False, default="user")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_UTCNOW)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=_UTCNOW,
        onupdate=_UTCNOW,
    )

    def full_name(self):
        return f"{self.last_name}, {self.first_name}"

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name(),
            "status": self.status,
            "user_type": self.user_type,
        }

    def active(self):
        return self.status == "active"

    def inactive(self):
        return self.status == "inactive"

    def deleted(self):
        return self.status == "deleted"

    def soft_delete(self):
        self.status = "deleted"
        db.session.commit()
