from flask import Flask

from app.storage import build_storage_service
from app.storage.services import AmazonStorageService


def _base_app():
    app = Flask(__name__)
    app.config["STORAGE_LOCAL_ROOT"] = "/tmp/ragflaskapi_test_storage"
    app.config["AWS_S3_BUCKET"] = "test-bucket"
    app.config["AWS_REGION"] = "us-east-1"
    app.config["AWS_ACCESS_KEY_ID"] = "test-access-key"
    app.config["AWS_SECRET_ACCESS_KEY"] = "test-secret-key"
    return app


def test_build_storage_service_uses_local_in_test_env(monkeypatch, tmp_path):
    monkeypatch.setenv("FLASK_ENV", "test")
    app = _base_app()
    app.config["AWS_S3_ENDPOINT"] = "http://localhost:4566"
    service = build_storage_service(app)
    assert isinstance(service, AmazonStorageService)


def test_build_storage_service_uses_amazon_in_development(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    app = _base_app()
    app.config["AWS_S3_ENDPOINT"] = "http://localhost:4566"
    service = build_storage_service(app)
    assert isinstance(service, AmazonStorageService)


def test_build_storage_service_uses_amazon_in_production(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    app = _base_app()
    app.config["AWS_S3_ENDPOINT"] = "http://localhost:4566"
    service = build_storage_service(app)
    assert isinstance(service, AmazonStorageService)
