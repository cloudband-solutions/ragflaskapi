from functools import wraps

from flask import g, jsonify, request

from app.helpers.api_helpers import decode_jwt
from app.models.user import User

def authenticate_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"message": "authentication required"}), 403

        parts = auth_header.split(" ")
        token = parts[1] if len(parts) > 1 else None
        if not token:
            return jsonify({"message": "invalid authorization"}), 403

        payload = decode_jwt(token)
        if not payload or "id" not in payload:
            return jsonify({"message": "invalid authorization"}), 403

        user = User.query.filter_by(id=payload["id"], status="active").first()
        if user is None:
            return jsonify({"message": "invalid authorization"}), 403

        g.current_user = user
        return func(*args, **kwargs)

    return wrapper


def authenticate_user_optional(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return func(*args, **kwargs)

        parts = auth_header.split(" ")
        token = parts[1] if len(parts) > 1 else None
        if not token:
            return jsonify({"message": "invalid authorization"}), 403

        payload = decode_jwt(token)
        if not payload or "id" not in payload:
            return jsonify({"message": "invalid authorization"}), 403

        user = User.query.filter_by(id=payload["id"], status="active").first()
        if user is None:
            return jsonify({"message": "invalid authorization"}), 403

        g.current_user = user
        return func(*args, **kwargs)

    return wrapper


def authorize_active(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = getattr(g, "current_user", None)
        if user is None or user.status == "inactive":
            return jsonify({"message": "unauthorized"}), 401
        return func(*args, **kwargs)

    return wrapper


def authorize_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = getattr(g, "current_user", None)
        if user is None or user.user_type != "admin":
            return jsonify({"message": "admin required"}), 403
        return func(*args, **kwargs)

    return wrapper
