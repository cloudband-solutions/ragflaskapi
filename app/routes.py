from flask import Blueprint

from app.controllers.health_controller import health
from app.controllers.system_controller import login as login_user
from app.controllers.users_controller import (
    create as create_user,
    delete as delete_user,
    index as list_users,
    show as show_user,
    update as update_user,
)

api_bp = Blueprint("api", __name__)


def register_routes(app):
    api_bp.add_url_rule("/health", view_func=health, methods=["GET"])
    api_bp.add_url_rule("/login", view_func=login_user, methods=["POST"])
    api_bp.add_url_rule("/users", view_func=list_users, methods=["GET"])
    api_bp.add_url_rule("/users", view_func=create_user, methods=["POST"])
    api_bp.add_url_rule("/users/<string:user_id>", view_func=show_user, methods=["GET"])
    api_bp.add_url_rule("/users/<string:user_id>", view_func=update_user, methods=["PUT"])
    api_bp.add_url_rule("/users/<string:user_id>", view_func=delete_user, methods=["DELETE"])

    app.register_blueprint(api_bp, url_prefix="/api")
