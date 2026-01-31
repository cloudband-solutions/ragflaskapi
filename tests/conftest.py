import os
import pytest

from sqlalchemy import text
from sqlalchemy.engine import make_url

os.environ.setdefault("FLASK_ENV", "test")

from app import create_app, db
from app.helpers.api_helpers import build_jwt_header, generate_jwt
from tests.factories import UserFactory


@pytest.fixture()
def app():
    app = create_app("tests.settings.TestConfig")
    with app.app_context():
        url = make_url(app.config.get("SQLALCHEMY_DATABASE_URI", ""))
        if url.get_backend_name() == "postgresql":
            db.session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            db.session.commit()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_headers():
    user = UserFactory()
    token = generate_jwt(user.to_dict())
    return build_jwt_header(token)
