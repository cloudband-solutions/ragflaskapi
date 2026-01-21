from flask import jsonify, request

from app.helpers.api_helpers import generate_jwt
from app.operations.system.login import Login


def login():
    payload = request.get_json(silent=True) or {}
    cmd = Login(email=payload.get("email"), password=payload.get("password"))
    cmd.execute()

    if cmd.valid():
        return jsonify({"token": generate_jwt(cmd.user.to_dict())})
    return jsonify(cmd.payload), 422
