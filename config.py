import os
from pathlib import Path

import re
import yaml


_ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")
_DEFAULT_DOCUMENT_TYPES = [
    "national_budget",
    "agency_budget",
    "project_program",
    "procurement_notice",
    "audit_report",
    "development_plan",
    "local_budget",
    "legislation_budget_related",
    "circular_guideline",
    "performance_report",
]


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


def _load_document_types():
    config_path = Path(os.getenv("DOCUMENT_TYPES_CONFIG", "document_types.yaml"))
    if not config_path.exists():
        return list(_DEFAULT_DOCUMENT_TYPES)
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("document_types"), list):
        return data["document_types"]
    return list(_DEFAULT_DOCUMENT_TYPES)


class Config:
    _db_config = _load_database_config()
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        _db_config.get("uri", "postgresql+psycopg2://localhost:5432/ragflaskapi"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "default-flask-api-secret")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "")
    AWS_REGION = os.getenv("AWS_REGION", "")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_ENDPOINT = os.getenv("AWS_S3_ENDPOINT", "")
    AWS_S3_PREFIX = os.getenv("AWS_S3_PREFIX", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    OPENAI_INFERENCE_MODEL = os.getenv("OPENAI_INFERENCE_MODEL", "")
    USE_OPENAI = os.getenv("USE_OPENAI", "true")
    DOCUMENT_TYPES = _load_document_types()
