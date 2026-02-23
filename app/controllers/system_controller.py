import os

from flask import current_app, jsonify, request

from app.helpers.api_helpers import generate_jwt
from app.operations.system.login import Login
from app.controllers.authenticated_controller import authenticate_user, authorize_active


def login():
    payload = request.get_json(silent=True) or {}
    cmd = Login(email=payload.get("email"), password=payload.get("password"))
    cmd.execute()

    if cmd.valid():
        return jsonify({"token": generate_jwt(cmd.user.to_dict())})
    return jsonify(cmd.payload), 422


@authenticate_user
@authorize_active
def environment():
    safe_keys = [
        "FLASK_ENV",
        "AUTHENTICATE_PUBLIC_DOCUMENTS",
        "DOCUMENT_TYPES_CONFIG",
        "AWS_REGION",
        "AWS_S3_BUCKET",
        "AWS_S3_ENDPOINT",
        "AWS_S3_PREFIX",
        "SQS_QUEUE_URL",
        "SQS_REGION",
        "AWS_SQS_ENDPOINT",
        "USE_OPENAI",
        "OPENAI_EMBEDDING_MODEL",
        "OPENAI_INFERENCE_MODEL",
        "LOCAL_EMBEDDING_MODEL_PATH",
        "LOCAL_EMBEDDING_N_CTX",
        "LOCAL_EMBEDDING_N_THREADS",
        "LOCAL_EMBEDDING_N_BATCH",
    ]
    payload = {}
    for key in safe_keys:
        value = current_app.config.get(key)
        if value is None:
            value = os.getenv(key)
        payload[key] = value
    return jsonify({"env": payload})
