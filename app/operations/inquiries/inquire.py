import logging
import os

from openai import OpenAI

from app.models.document_embedding import DocumentEmbedding
from app.operations.validator import Validator


DEFAULT_TOP_K = 5


class Inquire(Validator):
    def __init__(self, query=None, document_types=None, top_k=None, config=None):
        super().__init__()
        self.query = query
        self.document_types = document_types
        self.top_k = top_k if top_k is not None else DEFAULT_TOP_K
        self.config = config or {}
        self.payload = {}
        self.status_code = 422
        self._stream = None
        self._mimetype = "text/plain"

    @property
    def mimetype(self):
        return self._mimetype

    def execute(self):
        self._validate()
        if self.invalid():
            return

        if not self._openai_enabled():
            self._mark_error("OpenAI is disabled", status_code=503)
            return

        api_key = self.config.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        embedding_model = self.config.get("OPENAI_EMBEDDING_MODEL") or os.getenv(
            "OPENAI_EMBEDDING_MODEL"
        )
        inference_model = self.config.get("OPENAI_INFERENCE_MODEL") or os.getenv(
            "OPENAI_INFERENCE_MODEL"
        )

        if not api_key:
            self._mark_error("OPENAI_API_KEY is required", status_code=500)
            return
        if not embedding_model:
            self._mark_error("OPENAI_EMBEDDING_MODEL is required", status_code=500)
            return
        if not inference_model:
            self._mark_error("OPENAI_INFERENCE_MODEL is required", status_code=500)
            return

        client = OpenAI(api_key=api_key)
        embedding_response = client.embeddings.create(
            model=embedding_model, input=self.query
        )
        query_embedding = embedding_response.data[0].embedding
        LOGGER.info("Inquiry embedding: %s", query_embedding)
        print(f"Inquiry embedding: {query_embedding}")

        embeddings_query = DocumentEmbedding.query.filter(
            DocumentEmbedding.document_type.in_(self.document_types)
        )
        results = (
            embeddings_query.order_by(
                DocumentEmbedding.embedding.cosine_distance(query_embedding)
            )
            .limit(self.top_k)
            .all()
        )

        context_parts = [row.content for row in results if row.content]
        context = "\n\n---\n\n".join(context_parts) if context_parts else ""

        system_prompt = (
            "You are a helpful assistant. Use the provided context to answer the question. "
            "If the context is insufficient, say you don't have enough information."
        )
        user_prompt = f"Context:\n{context}\n\nQuestion: {self.query}"

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

        self._stream = generate

    def stream(self):
        if self._stream is None:
            return iter(())
        return self._stream()

    def _validate(self):
        if not self.query:
            self._mark_error("query is required")
            return

        if not isinstance(self.document_types, list) or not self.document_types:
            self._mark_error("document_types must be a non-empty array")
            return

        if not isinstance(self.top_k, int) or self.top_k <= 0:
            self._mark_error("k must be a positive integer")
            return

        allowed_types = self.config.get("DOCUMENT_TYPES")
        if isinstance(allowed_types, list):
            invalid_types = [
                item for item in self.document_types if item not in allowed_types
            ]
            if invalid_types:
                self._mark_error(
                    "document_types contains unsupported values",
                    invalid_types=invalid_types,
                )
                return

    def _openai_enabled(self):
        return str(self.config.get("USE_OPENAI", "true")).lower() in {
            "1",
            "true",
            "yes",
            "y",
        }

    def _mark_error(self, message, status_code=422, invalid_types=None):
        self.payload = {"message": message}
        if invalid_types:
            self.payload["invalid_types"] = invalid_types
        self.status_code = status_code
        self.num_errors = 1
LOGGER = logging.getLogger(__name__)
