import re

from app import db
from app.helpers.api_helpers import build_password_hash
from app.models.user import User
from app.operations.validator import Validator


EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


class Save(Validator):
    def __init__(
        self,
        email=None,
        first_name=None,
        last_name=None,
        password=None,
        password_confirmation=None,
        user=None,
        user_type=None,
        document_types=None,
        allowed_document_types=None,
    ):
        super().__init__()

        self.user = user
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.password_confirmation = password_confirmation
        self.user_type = user_type
        self.document_types = document_types
        self.allowed_document_types = allowed_document_types or []

        self.payload = {
            "email": [],
            "first_name": [],
            "last_name": [],
            "password": [],
            "password_confirmation": [],
        }

    def execute(self):
        self._validate()

        if self.valid():
            if self.user is None:
                self.user = User(
                    email=self.email,
                    first_name=self.first_name,
                    last_name=self.last_name,
                    password_hash=build_password_hash(self.password),
                    user_type=self.user_type or "user",
                    document_types=self.document_types,
                )
                db.session.add(self.user)
            else:
                if self.email:
                    self.user.email = self.email
                if self.first_name:
                    self.user.first_name = self.first_name
                if self.last_name:
                    self.user.last_name = self.last_name
                if self.user_type:
                    self.user.user_type = self.user_type
                if self.document_types is not None:
                    self.user.document_types = self.document_types

            db.session.commit()

    def _validate(self):
        if self.user is None:
            if not self.email:
                self.payload["email"].append("required")
            elif not EMAIL_REGEX.match(self.email):
                self.payload["email"].append("invalid format")
            elif User.query.filter_by(email=self.email).first() is not None:
                self.payload["email"].append("already taken")

            if not self.first_name:
                self.payload["first_name"].append("required")

            if not self.last_name:
                self.payload["last_name"].append("required")

            if not self.password:
                self.payload["password"].append("required")

            if not self.password_confirmation:
                self.payload["password_confirmation"].append("required")

            if (
                self.password
                and self.password_confirmation
                and self.password != self.password_confirmation
            ):
                self.payload["password"].append("does not match")
                self.payload["password_confirmation"].append("does not match")
        else:
            if self.email:
                existing = (
                    User.query.filter(User.id != self.user.id)
                    .filter_by(email=self.email)
                    .first()
                )
                if existing is not None:
                    self.payload["email"].append("already taken")
                elif not EMAIL_REGEX.match(self.email):
                    self.payload["email"].append("invalid format")

        if self.user_type and self.user_type not in {"user", "admin", "ops"}:
            self.payload.setdefault("user_type", []).append("invalid type")

        if self.document_types is not None:
            if not isinstance(self.document_types, list):
                self.payload.setdefault("document_types", []).append("must be a list")
            else:
                invalid = [
                    item
                    for item in self.document_types
                    if item not in self.allowed_document_types
                ]
                if invalid:
                    self.payload.setdefault("document_types", []).append("invalid values")

        self.count_errors()
