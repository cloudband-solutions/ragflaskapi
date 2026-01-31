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
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "")
    AWS_REGION = os.getenv("AWS_REGION", "")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_ENDPOINT = os.getenv("AWS_S3_ENDPOINT", "http://localhost:4566")
    AWS_S3_PREFIX = os.getenv("AWS_S3_PREFIX", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "test-openai-key")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    OPENAI_INFERENCE_MODEL = os.getenv("OPENAI_INFERENCE_MODEL", "gpt-4.1-mini")
    USE_OPENAI = os.getenv("USE_OPENAI", "true")
