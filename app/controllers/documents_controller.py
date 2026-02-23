from functools import wraps

from flask import current_app, jsonify, request, g

from app import db
from app.controllers.authenticated_controller import (
    authenticate_user,
    authenticate_user_optional,
    authorize_active,
    authorize_admin,
)
from sqlalchemy import false
from app.models.document import Document
from app.models.document_embedding import DocumentEmbedding
from app.operations.documents.save import Save as SaveDocument
from app.operations.documents.enqueue_embedding import EnqueueEmbedding
from app.storage import get_storage


ITEMS_PER_PAGE = 20


def _get_payload():
    data = request.get_json(silent=True)
    if data is not None:
        return data
    if request.form:
        return request.form
    return {}


def _public_document_payload(document, has_embeddings=False):
    return {
        "id": document.id,
        "name": document.name,
        "description": document.description,
        "document_type": document.document_type,
        "original_filename": document.original_filename,
        "content_type": document.content_type,
        "size_bytes": document.size_bytes,
        "download_url": get_storage().url(document.storage_key),
        "embedding_status": document.embedding_status,
        "enqueue_error": document.enqueue_error,
        "embedding_error": document.embedding_error,
        "has_embeddings": has_embeddings,
    }


def _document_embedding_ids(documents):
    ids = [document.id for document in documents]
    if not ids:
        return set()
    rows = (
        db.session.query(DocumentEmbedding.document_id)
        .filter(DocumentEmbedding.document_id.in_(ids))
        .distinct()
        .all()
    )
    return {row[0] for row in rows}


def _available_document_types():
    allowed_types = current_app.config.get("DOCUMENT_TYPES") or []
    if allowed_types:
        return sorted(set(allowed_types))
    query = (
        db.session.query(Document.document_type)
        .filter(Document.document_type.isnot(None))
        .filter(Document.document_type != "")
    )
    rows = query.distinct().order_by(Document.document_type.asc()).all()
    return [row[0] for row in rows]


def _authenticate_public_documents_enabled():
    return str(
        current_app.config.get("AUTHENTICATE_PUBLIC_DOCUMENTS", "false")
    ).lower() in {"1", "true", "yes", "y"}


def _maybe_authenticate_public_documents(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if _authenticate_public_documents_enabled():
            return authenticate_user(authorize_active(func))(*args, **kwargs)
        return authenticate_user_optional(func)(*args, **kwargs)

    return wrapper


def _allowed_document_types_for_user(user):
    allowed_types = current_app.config.get("DOCUMENT_TYPES") or []
    if user is None:
        return allowed_types
    return user.allowed_document_types(allowed_types)


def _apply_user_document_type_filter(query, user):
    allowed_types = _allowed_document_types_for_user(user)
    if allowed_types is None:
        return query
    if allowed_types:
        return query.filter(Document.document_type.in_(allowed_types))
    return query.filter(false())


@_maybe_authenticate_public_documents
def public_index():
    documents_query = Document.query.order_by(Document.created_at.desc())
    user = getattr(g, "current_user", None)
    documents_query = _apply_user_document_type_filter(documents_query, user)

    query = request.args.get("query")
    if query:
        pattern = f"%{query}%"
        documents_query = documents_query.filter(Document.name.ilike(pattern))

    document_type = request.args.get("document_type")
    if document_type:
        documents_query = documents_query.filter_by(document_type=document_type)

    embedding_status = request.args.get("embedding_status")
    if embedding_status:
        documents_query = documents_query.filter_by(embedding_status=embedding_status)

    page = request.args.get("page", type=int) or 1
    per_page = request.args.get("per_page", type=int) or ITEMS_PER_PAGE
    total = documents_query.count()
    total_pages = max((total + per_page - 1) // per_page, 1)

    documents = (
        documents_query.offset((page - 1) * per_page).limit(per_page).all()
        if total > 0
        else []
    )

    embedding_ids = _document_embedding_ids(documents)
    records = [
        _public_document_payload(document, document.id in embedding_ids)
        for document in documents
    ]

    return jsonify(
        {
            "records": records,
            "total_pages": total_pages,
            "current_page": page,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None,
        }
    )


@_maybe_authenticate_public_documents
def public_document_types():
    user = getattr(g, "current_user", None)
    return jsonify({"document_types": _allowed_document_types_for_user(user)})


@_maybe_authenticate_public_documents
def public_show(document_id):
    document = db.session.get(Document, document_id)
    if document is None:
        return jsonify({"message": "not found"}), 404
    user = getattr(g, "current_user", None)
    allowed_types = _allowed_document_types_for_user(user)
    if allowed_types is not None and allowed_types:
        if document.document_type not in allowed_types:
            return jsonify({"message": "unauthorized"}), 403
    elif allowed_types == []:
        return jsonify({"message": "unauthorized"}), 403
    has_embeddings = (
        db.session.query(DocumentEmbedding.document_id)
        .filter(DocumentEmbedding.document_id == document.id)
        .first()
        is not None
    )
    return jsonify(_public_document_payload(document, has_embeddings))


@authenticate_user
@authorize_active
@authorize_admin
def document_types():
    return jsonify({"document_types": _available_document_types()})


@_maybe_authenticate_public_documents
def index():
    documents_query = Document.query.order_by(Document.created_at.desc())

    query = request.args.get("query")
    if query:
        pattern = f"%{query}%"
        documents_query = documents_query.filter(Document.name.ilike(pattern))

    document_type = request.args.get("document_type")
    if document_type:
        documents_query = documents_query.filter_by(document_type=document_type)

    embedding_status = request.args.get("embedding_status")
    if embedding_status:
        documents_query = documents_query.filter_by(embedding_status=embedding_status)

    page = request.args.get("page", type=int) or 1
    per_page = request.args.get("per_page", type=int) or ITEMS_PER_PAGE
    total = documents_query.count()
    total_pages = max((total + per_page - 1) // per_page, 1)

    documents = (
        documents_query.offset((page - 1) * per_page).limit(per_page).all()
        if total > 0
        else []
    )

    embedding_ids = _document_embedding_ids(documents)
    records = [
        {**document.to_dict(), "has_embeddings": document.id in embedding_ids}
        for document in documents
    ]

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
def show(document_id):
    document = db.session.get(Document, document_id)
    if document is None:
        return jsonify({"message": "not found"}), 404
    return jsonify(document.to_dict())


@authenticate_user
@authorize_active
@authorize_admin
def create():
    payload = _get_payload()
    cmd = SaveDocument(
        name=payload.get("name"),
        description=payload.get("description"),
        document_type=payload.get("document_type"),
        upload=request.files.get("file"),
    )
    cmd.execute()

    if cmd.valid():
        return jsonify(cmd.document.to_dict())
    return jsonify({"message": cmd.message}), 422


@authenticate_user
@authorize_active
@authorize_admin
def update(document_id):
    document = db.session.get(Document, document_id)
    if document is None:
        return jsonify({"message": "not found"}), 404

    payload = _get_payload()
    cmd = SaveDocument(
        document=document,
        name=payload.get("name"),
        description=payload.get("description"),
        document_type=payload.get("document_type"),
        upload=request.files.get("file"),
        name_present="name" in payload,
        description_present="description" in payload,
        document_type_present="document_type" in payload,
    )
    cmd.execute()

    if cmd.valid():
        return jsonify(cmd.document.to_dict())
    return jsonify({"message": cmd.message}), 422


@authenticate_user
@authorize_active
@authorize_admin
def delete(document_id):
    document = db.session.get(Document, document_id)
    if document is None:
        return jsonify({"message": "not found"}), 404

    cmd = SaveDocument(document=document)
    cmd.delete()

    return jsonify({"message": "ok"})


@authenticate_user
@authorize_active
@authorize_admin
def retry_enqueue(document_id):
    document = db.session.get(Document, document_id)
    if document is None:
        return jsonify({"message": "not found"}), 404
    if document.embedding_status != "failed":
        return (
            jsonify({"message": "document is not in failed embedding status"}),
            422,
        )

    EnqueueEmbedding(document=document).execute()
    return jsonify(document.to_dict())
