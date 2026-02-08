from app import db
from app.models.document_embedding import DocumentEmbedding
from tests.factories import DocumentFactory


def test_list_documents(client, auth_headers):
    DocumentFactory.create_batch(2)
    response = client.get("/documents", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json["records"]) == 2


def test_list_documents_includes_embeddings_flag(client, auth_headers):
    document = DocumentFactory()
    DocumentFactory()

    embedding = DocumentEmbedding(
        document_id=document.id,
        embedding=[0.1, 0.2, 0.3],
        chunk_index=0,
        content="chunk",
    )
    db.session.add(embedding)
    db.session.commit()

    response = client.get("/documents", headers=auth_headers)
    assert response.status_code == 200

    records = response.json["records"]
    assert len(records) == 2
    record_by_id = {record["id"]: record for record in records}
    assert record_by_id[document.id]["has_embeddings"] is True
    other_id = next(
        record_id for record_id in record_by_id.keys() if record_id != document.id
    )
    assert record_by_id[other_id]["has_embeddings"] is False
