import os

from flask import Response, current_app, jsonify, request, stream_with_context
from openai import OpenAI

from app import db
from app.models.document_embedding import DocumentEmbedding


DEFAULT_TOP_K = 5


def inquire():
    payload = request.get_json(silent=True) or {}
    query = payload.get("query")
    document_types = payload.get("document_types")
    top_k = payload.get("k", DEFAULT_TOP_K)

    if not query:
        return jsonify({"message": "query is required"}), 422
    if not isinstance(document_types, list) or not document_types:
        return jsonify({"message": "document_types must be a non-empty array"}), 422
    if not isinstance(top_k, int) or top_k <= 0:
        return jsonify({"message": "k must be a positive integer"}), 422

    if str(current_app.config.get("USE_OPENAI", "true")).lower() not in {
        "1",
        "true",
        "yes",
        "y",
    }:
        return jsonify({"message": "OpenAI is disabled"}), 503

    api_key = current_app.config.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    embedding_model = current_app.config.get("OPENAI_EMBEDDING_MODEL") or os.getenv(
        "OPENAI_EMBEDDING_MODEL"
    )
    inference_model = current_app.config.get("OPENAI_INFERENCE_MODEL") or os.getenv(
        "OPENAI_INFERENCE_MODEL"
    )

    if not api_key:
        return jsonify({"message": "OPENAI_API_KEY is required"}), 500
    if not embedding_model:
        return jsonify({"message": "OPENAI_EMBEDDING_MODEL is required"}), 500
    if not inference_model:
        return jsonify({"message": "OPENAI_INFERENCE_MODEL is required"}), 500

    client = OpenAI(api_key=api_key)
    embedding_response = client.embeddings.create(model=embedding_model, input=query)
    query_embedding = embedding_response.data[0].embedding

    embeddings_query = DocumentEmbedding.query.filter(
        DocumentEmbedding.document_type.in_(document_types)
    )
    results = (
        embeddings_query.order_by(
            DocumentEmbedding.embedding.cosine_distance(query_embedding)
        )
        .limit(top_k)
        .all()
    )

    context_parts = [row.content for row in results if row.content]
    context = "\n\n---\n\n".join(context_parts) if context_parts else ""

    system_prompt = (
        "You are a helpful assistant. Use the provided context to answer the question. "
        "If the context is insufficient, say you don't have enough information."
    )
    user_prompt = f"Context:\n{context}\n\nQuestion: {query}"

    def generate():
        stream = client.responses.create(
            model=inference_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
        )
        for event in stream:
            if event.type == "response.output_text.delta":
                yield event.delta

    return Response(stream_with_context(generate()), mimetype="text/plain")
