from flask import Response, current_app, jsonify, request, stream_with_context, g

from app.controllers.authenticated_controller import authenticate_user, authorize_active
from app.operations.inquiries.inquire import Inquire


@authenticate_user
@authorize_active
def inquire():
    payload = request.get_json(silent=True) or {}
    allowed_types = g.current_user.allowed_document_types(
        current_app.config.get("DOCUMENT_TYPES") or []
    )
    requested_types = payload.get("document_types")
    if not isinstance(requested_types, list) or not requested_types:
        return jsonify({"message": "document_types must be a non-empty array"}), 422

    invalid_types = [
        doc_type for doc_type in requested_types if doc_type not in allowed_types
    ]
    if invalid_types:
        return (
            jsonify(
                {"message": "document_types contains unsupported values", "invalid_types": invalid_types}
            ),
            403,
        )
    cmd = Inquire(
        query=payload.get("query"),
        document_types=requested_types,
        top_k=payload.get("k"),
        config=current_app.config,
    )
    cmd.execute()

    if cmd.invalid():
        return jsonify(cmd.payload), cmd.status_code

    return Response(stream_with_context(cmd.stream()), mimetype=cmd.mimetype)
