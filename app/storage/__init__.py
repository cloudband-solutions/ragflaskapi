import os

from flask import current_app

from app.storage.services import AmazonStorageService


def _environment_for(app):
    return os.getenv("FLASK_ENV", app.config.get("FLASK_ENV", "development"))


def build_storage_service(app):
    env = _environment_for(app)
    if env not in {"test", "development", "production"}:
        raise ValueError(f"Unsupported environment for storage: {env}")
    return AmazonStorageService(
        bucket=app.config.get("AWS_S3_BUCKET", ""),
        region=app.config.get("AWS_REGION", ""),
        access_key_id=app.config.get("AWS_ACCESS_KEY_ID", ""),
        secret_access_key=app.config.get("AWS_SECRET_ACCESS_KEY", ""),
        endpoint_url=app.config.get("AWS_S3_ENDPOINT", "") or None,
        prefix=app.config.get("AWS_S3_PREFIX", "") or None,
    )


def init_storage(app):
    app.extensions["storage"] = build_storage_service(app)


def get_storage():
    return current_app.extensions["storage"]
