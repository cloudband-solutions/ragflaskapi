import factory
from werkzeug.security import generate_password_hash

from app import db
from app.models.document import Document
from app.models.user import User


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Sequence(lambda n: f"First{n}")
    last_name = factory.Sequence(lambda n: f"Last{n}")
    password_hash = factory.LazyFunction(lambda: generate_password_hash("password"))
    status = "active"


class DocumentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Document
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Document {n}")
    description = factory.Faker("sentence")
    document_type = factory.Faker("word")
    original_filename = factory.Sequence(lambda n: f"document-{n}.pdf")
    storage_key = factory.Sequence(lambda n: f"documents/document-{n}.pdf")
    storage_provider = "s3"
    content_type = "application/pdf"
    size_bytes = factory.Faker("random_int", min=1000, max=10_000_000)
