from flask import Response, current_app, jsonify, request, stream_with_context

from app.operations.inquiries.inquire import Inquire


def inquire():
    payload = request.get_json(silent=True) or {}
    cmd = Inquire(
        query=payload.get("query"),
        document_types=payload.get("document_types"),
        top_k=payload.get("k"),
        config=current_app.config,
    )
    cmd.execute()

    if cmd.invalid():
        return jsonify(cmd.payload), cmd.status_code

    return Response(stream_with_context(cmd.stream()), mimetype=cmd.mimetype)
