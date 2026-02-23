from flask import jsonify, request
from sqlalchemy import or_

from app import db
from app.controllers.authenticated_controller import (
    authenticate_user,
    authorize_active,
    authorize_admin,
)
from app.models.user import User
from app.operations.users.save import Save as SaveUser


ITEMS_PER_PAGE = 20


def _get_payload():
    data = request.get_json(silent=True)
    if data is not None:
        return data
    if request.form:
        return request.form
    return {}


@authenticate_user
@authorize_active
@authorize_admin
def index():
    users_query = User.query.order_by(User.last_name.asc())

    query = request.args.get("query")
    if query:
        pattern = f"%{query}%"
        users_query = users_query.filter(
            or_(
                User.first_name.ilike(pattern),
                User.last_name.ilike(pattern),
                User.email.ilike(pattern),
            )
        )

    status = request.args.get("status")
    if status:
        users_query = users_query.filter_by(status=status)

    page = request.args.get("page", type=int) or 1
    per_page = request.args.get("per_page", type=int) or ITEMS_PER_PAGE
    total = users_query.count()
    total_pages = max((total + per_page - 1) // per_page, 1)

    users = (
        users_query.offset((page - 1) * per_page).limit(per_page).all()
        if total > 0
        else []
    )

    records = [user.to_dict() for user in users]

    return jsonify(
        {
            "records": records,
            "total_pages": total_pages,
            "current_page": page,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None,
        }
    )


@authenticate_user
@authorize_active
@authorize_admin
def show(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"message": "not found"}), 404
    return jsonify(user.to_dict())


@authenticate_user
@authorize_active
@authorize_admin
def create():
    payload = _get_payload()
    cmd = SaveUser(
        email=payload.get("email"),
        first_name=payload.get("first_name"),
        last_name=payload.get("last_name"),
        password=payload.get("password"),
        password_confirmation=payload.get("password_confirmation"),
    )
    cmd.execute()

    if cmd.valid():
        return jsonify(cmd.user.to_dict())
    return jsonify(cmd.payload), 422


@authenticate_user
@authorize_active
@authorize_admin
def update(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"message": "not found"}), 404

    payload = _get_payload()
    cmd = SaveUser(
        user=user,
        email=payload.get("email"),
        first_name=payload.get("first_name"),
        last_name=payload.get("last_name"),
        password=payload.get("password"),
        password_confirmation=payload.get("password_confirmation"),
    )
    cmd.execute()

    if cmd.valid():
        return jsonify(cmd.user.to_dict())
    return jsonify(cmd.payload), 422


@authenticate_user
@authorize_active
@authorize_admin
def delete(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"message": "not found"}), 404

    user.soft_delete()
    db.session.refresh(user)

    return jsonify({"message": "ok"})
