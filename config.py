import os
from pathlib import Path

import re
import yaml


_ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")


def _expand_env_vars(value):
    if not isinstance(value, str):
        return value

    def _replace(match):
        return os.getenv(match.group(1), "")

    return _ENV_PATTERN.sub(_replace, value)


def _load_database_config():
    config_path = Path(os.getenv("DATABASE_YAML", "database.yaml"))
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    env = os.getenv("FLASK_ENV", "development")
    config = data.get(env, {})
    return {key: _expand_env_vars(value) for key, value in config.items()}


class Config:
    _db_config = _load_database_config()
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        _db_config.get("uri", "postgresql+psycopg2://localhost:5432/ragflaskapi"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "default-flask-api-secret")
    STORAGE_LOCAL_ROOT = os.getenv("STORAGE_LOCAL_ROOT", "storage")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "")
    AWS_REGION = os.getenv("AWS_REGION", "")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_ENDPOINT = os.getenv("AWS_S3_ENDPOINT", "")
    AWS_S3_PREFIX = os.getenv("AWS_S3_PREFIX", "")
