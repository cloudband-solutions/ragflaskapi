from flask import jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import db

def health():
    payload = {"status": "ok", "database": {"status": "ok"}}
    status_code = 200

    try:
        db.session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        payload["status"] = "degraded"
        payload["database"]["status"] = "error"
        status_code = 503

    return jsonify(payload), status_code
