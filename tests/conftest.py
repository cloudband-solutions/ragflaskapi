import pytest

from app import create_app, db
from app.helpers.api_helpers import build_jwt_header, generate_jwt
from tests.factories import UserFactory


@pytest.fixture()
def app():
    app = create_app("tests.settings.TestConfig")
    with app.app_context():
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
