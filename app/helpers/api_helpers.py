from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash


def build_password_hash(password):
    return generate_password_hash(password)


def password_match(password, password_hash):
    return check_password_hash(password_hash, password)


def build_jwt_header(token):
    return {"Authorization": f"Bearer {token}"}


def generate_jwt(user_object):
    payload = dict(user_object)
    payload["exp"] = datetime.now(timezone.utc) + timedelta(days=60)
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_jwt(token):
    try:
        return jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
    except jwt.PyJWTError:
        return None
