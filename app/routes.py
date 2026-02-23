from flask import Blueprint

from app.controllers.health_controller import health
from app.controllers.system_controller import login as login_user
from app.controllers.documents_controller import (
    create as create_document,
    delete as delete_document,
    index as list_documents,
    public_document_types as public_document_types,
    public_index as public_list_documents,
    retry_enqueue as retry_document_enqueue,
    show as show_document,
    update as update_document,
)
from app.controllers.inquiries_controller import inquire
from app.controllers.users_controller import (
    create as create_user,
    delete as delete_user,
    index as list_users,
    show as show_user,
    update as update_user,
)

def register_routes(app):
    api_bp = Blueprint("/", __name__)
    api_bp.add_url_rule("/health", view_func=health, methods=["GET"], endpoint="health")
    api_bp.add_url_rule("/login", view_func=login_user, methods=["POST"], endpoint="login")
    api_bp.add_url_rule("/users", view_func=list_users, methods=["GET"], endpoint="users_index")
    api_bp.add_url_rule("/users", view_func=create_user, methods=["POST"], endpoint="users_create")
    api_bp.add_url_rule("/users/<string:user_id>", view_func=show_user, methods=["GET"], endpoint="users_show")
    api_bp.add_url_rule("/users/<string:user_id>", view_func=update_user, methods=["PUT"], endpoint="users_update")
    api_bp.add_url_rule("/users/<string:user_id>", view_func=delete_user, methods=["DELETE"], endpoint="users_delete")
    api_bp.add_url_rule("/documents", view_func=list_documents, methods=["GET"], endpoint="documents_index")
    api_bp.add_url_rule("/public/documents", view_func=public_list_documents, methods=["GET"], endpoint="public_documents_index")
    api_bp.add_url_rule(
        "/public/document_types", view_func=public_document_types, methods=["GET"], endpoint="public_document_types"
    )
    api_bp.add_url_rule("/documents", view_func=create_document, methods=["POST"], endpoint="documents_create")
    api_bp.add_url_rule(
        "/documents/<string:document_id>", view_func=show_document, methods=["GET"], endpoint="documents_show"
    )
    api_bp.add_url_rule(
        "/documents/<string:document_id>", view_func=update_document, methods=["PUT"], endpoint="documents_update"
    )
    api_bp.add_url_rule(
        "/documents/<string:document_id>", view_func=delete_document, methods=["DELETE"], endpoint="documents_delete"
    )
    api_bp.add_url_rule(
        "/documents/<string:document_id>/enqueue",
        view_func=retry_document_enqueue,
        methods=["POST"],
        endpoint="documents_enqueue",
    )
    api_bp.add_url_rule("/inquire", view_func=inquire, methods=["POST"], endpoint="inquire")

    app.register_blueprint(api_bp)
