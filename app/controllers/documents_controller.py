from uuid import uuid4

from flask import jsonify, request
from sqlalchemy.exc import IntegrityError

from app import db
from app.controllers.authenticated_controller import authenticate_user, authorize_active
from app.models.document import Document
from app.storage import get_storage


ITEMS_PER_PAGE = 20


def _get_payload():
    data = request.get_json(silent=True)
    if data is not None:
        return data
    if request.form:
        return request.form
    return {}


def _file_size(file):
    try:
        current = file.stream.tell()
        file.stream.seek(0, 2)
        size = file.stream.tell()
        file.stream.seek(current)
        return size
    except (AttributeError, OSError):
        return None


@authenticate_user
@authorize_active
def index():
    documents_query = Document.query.order_by(Document.created_at.desc())

    query = request.args.get("query")
    if query:
        pattern = f"%{query}%"
        documents_query = documents_query.filter(Document.name.ilike(pattern))

    document_type = request.args.get("document_type")
    if document_type:
        documents_query = documents_query.filter_by(document_type=document_type)

    page = request.args.get("page", type=int) or 1
    per_page = request.args.get("per_page", type=int) or ITEMS_PER_PAGE
    total = documents_query.count()
    total_pages = max((total + per_page - 1) // per_page, 1)

    documents = (
        documents_query.offset((page - 1) * per_page).limit(per_page).all()
        if total > 0
        else []
    )

    records = [document.to_dict() for document in documents]

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
def create():
    payload = _get_payload()
    name = payload.get("name")
    if not name:
        return jsonify({"message": "name is required"}), 422

    if Document.query.filter_by(name=name).first() is not None:
        return jsonify({"message": "name must be unique"}), 422

    upload = request.files.get("file")
    if upload is None:
        return jsonify({"message": "file is required"}), 422
    filename = upload.filename or ""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in {"txt", "pdf"}:
        return jsonify({"message": "unsupported file type"}), 422

    storage_key = str(uuid4())
    content_type = upload.mimetype
    size_bytes = _file_size(upload)
    storage = get_storage()

    storage.save(storage_key, upload, content_type=content_type)

    document = Document(
        name=name,
        description=payload.get("description"),
        document_type=payload.get("document_type"),
        original_filename=upload.filename or name,
        storage_key=storage_key,
        storage_provider="s3",
        content_type=content_type,
        size_bytes=size_bytes,
    )

    try:
        db.session.add(document)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        storage.delete(storage_key)
        return jsonify({"message": "name must be unique"}), 422

    return jsonify(document.to_dict())


@authenticate_user
@authorize_active
def update(document_id):
    document = db.session.get(Document, document_id)
    if document is None:
        return jsonify({"message": "not found"}), 404

    payload = _get_payload()

    if "name" in payload and payload.get("name") != document.name:
        name = payload.get("name")
        if not name:
            return jsonify({"message": "name is required"}), 422
        if Document.query.filter_by(name=name).first() is not None:
            return jsonify({"message": "name must be unique"}), 422
        document.name = name

    if "description" in payload:
        document.description = payload.get("description")
    if "document_type" in payload:
        document.document_type = payload.get("document_type")

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "name must be unique"}), 422

    return jsonify(document.to_dict())


@authenticate_user
@authorize_active
def delete(document_id):
    document = db.session.get(Document, document_id)
    if document is None:
        return jsonify({"message": "not found"}), 404

    storage = get_storage()
    storage.delete(document.storage_key)

    db.session.delete(document)
    db.session.commit()

    return jsonify({"message": "ok"})
