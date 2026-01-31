import os

from config import _load_database_config

os.environ.setdefault("FLASK_ENV", "test")
_db_config = _load_database_config()


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = _db_config.get(
        "uri", "postgresql+psycopg2://localhost:5432/ragflaskapi_test"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test-secret-32-bytes-minimum-key"
