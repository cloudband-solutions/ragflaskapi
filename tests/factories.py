import factory
from werkzeug.security import generate_password_hash

from app import db
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
