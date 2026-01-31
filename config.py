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
        _db_config.get("uri", "postgresql+psycopg2://localhost:5432/default_flask_api"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "default-flask-api-secret")
