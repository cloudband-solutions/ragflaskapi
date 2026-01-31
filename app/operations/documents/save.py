from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from app import db
from app.models.document import Document
from app.operations.validator import Validator
from app.storage import get_storage


ALLOWED_EXTENSIONS = {"pdf", "txt"}


class Save(Validator):
    def __init__(
        self,
        name=None,
        description=None,
        document_type=None,
        upload=None,
        document=None,
        name_present=False,
        description_present=False,
        document_type_present=False,
    ):
        super().__init__()

        self.document = document
        self.name = name
        self.description = description
        self.document_type = document_type
        self.upload = upload
        self.name_present = name_present
        self.description_present = description_present
        self.document_type_present = document_type_present

        self.payload = {"message": []}
        self.message = None

    def execute(self):
        self._validate()
        if self.valid():
            if self.document is None:
                self._create_document()
            else:
                self._update_document()

    def delete(self):
        if self.document is None:
            return

        storage = get_storage()
        storage.delete(self.document.storage_key)

        db.session.delete(self.document)
        db.session.commit()

    def _validate(self):
        if self.document is None:
            if not self.name:
                self._mark_invalid("name is required")
                return
            if Document.query.filter_by(name=self.name).first() is not None:
                self._mark_invalid("name must be unique")
                return
            if self.upload is None:
                self._mark_invalid("file is required")
                return
            if not self._allowed_extension(self.upload.filename or ""):
                self._mark_invalid("unsupported file type")
                return
        elif self.name_present and self.name != self.document.name:
            if not self.name:
                self._mark_invalid("name is required")
                return
            existing = (
                Document.query.filter(Document.id != self.document.id)
                .filter_by(name=self.name)
                .first()
            )
            if existing is not None:
                self._mark_invalid("name must be unique")
                return

    def _create_document(self):
        storage_key = str(uuid4())
        content_type = self.upload.mimetype
        size_bytes = self._file_size(self.upload)
        storage = get_storage()

        storage.save(storage_key, self.upload, content_type=content_type)

        self.document = Document(
            name=self.name,
            description=self.description,
            document_type=self.document_type,
            original_filename=self.upload.filename or self.name,
            storage_key=storage_key,
            storage_provider="s3",
            content_type=content_type,
            size_bytes=size_bytes,
        )

        try:
            db.session.add(self.document)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            storage.delete(storage_key)
            self._mark_invalid("name must be unique")

    def _update_document(self):
        if self.name_present and self.name != self.document.name:
            self.document.name = self.name
        if self.description_present:
            self.document.description = self.description
        if self.document_type_present:
            self.document.document_type = self.document_type

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            self._mark_invalid("name must be unique")

    def _allowed_extension(self, filename):
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        return extension in ALLOWED_EXTENSIONS

    def _file_size(self, file):
        try:
            current = file.stream.tell()
            file.stream.seek(0, 2)
            size = file.stream.tell()
            file.stream.seek(current)
            return size
        except (AttributeError, OSError):
            return None

    def _mark_invalid(self, message):
        self.payload["message"] = [message]
        self.message = message
        self.num_errors = 1
