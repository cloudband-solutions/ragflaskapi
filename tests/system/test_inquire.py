from types import SimpleNamespace

from app import db
from app.models.document_embedding import DocumentEmbedding
from tests.factories import DocumentFactory


class FakeEmbeddings:
    def create(self, model, input):
        return SimpleNamespace(data=[SimpleNamespace(embedding=[0.1, 0.2, 0.3])])


class FakeResponses:
    def create(self, model, input, stream=False):
        return [
            SimpleNamespace(type="response.output_text.delta", delta="Hello"),
            SimpleNamespace(type="response.output_text.delta", delta=" world"),
        ]


class FakeOpenAI:
    def __init__(self, api_key=None):
        self.embeddings = FakeEmbeddings()
        self.responses = FakeResponses()


def test_inquire_requires_query_and_document_types(client):
    response = client.post("/inquire", json={"document_types": ["policy"]})
    assert response.status_code == 422
    assert response.json == {"message": "query is required"}

    response = client.post("/inquire", json={"query": "hello"})
    assert response.status_code == 422
    assert response.json == {"message": "document_types must be a non-empty array"}


def test_inquire_streams_response(client, monkeypatch):
    monkeypatch.setattr(
        "app.controllers.inquiries_controller.OpenAI", FakeOpenAI
    )

    document = DocumentFactory(document_type="policy")
    db.session.add(
        DocumentEmbedding(
            document_id=document.id,
            document_type=document.document_type,
            embedding=[0.1, 0.2, 0.3],
            chunk_index=0,
            content="Policy content.",
        )
    )
    db.session.commit()

    response = client.post(
        "/inquire",
        json={"query": "What is the policy?", "document_types": ["policy"], "k": 1},
    )
    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Hello world"
