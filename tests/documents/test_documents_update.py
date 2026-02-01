import io

from app.models.document import Document
from tests.factories import DocumentFactory


def test_update_document_valid(client, auth_headers):
    document = DocumentFactory()
    payload = {"name": "Updated name", "description": "Updated description"}
    response = client.put(
        f"/documents/{document.id}", json=payload, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json["name"] == payload["name"]
    assert response.json["description"] == payload["description"]


def test_update_document_unique_name(client, auth_headers):
    document = DocumentFactory(name="Doc 1")
    other = DocumentFactory(name="Doc 2")
    response = client.put(
        f"/documents/{other.id}", json={"name": document.name}, headers=auth_headers
    )
    assert response.status_code == 422
    assert response.json["message"] == "name must be unique"


def test_update_document_with_file(client, auth_headers):
    payload = {
        "name": "Doc A",
        "description": "Original description",
        "document_type": "pdf",
        "file": (io.BytesIO(b"original"), "original.pdf"),
    }
    response = client.post(
        "/documents", data=payload, headers=auth_headers, content_type="multipart/form-data"
    )
    assert response.status_code == 200
    original_key = response.json["storage_key"]

    update_payload = {
        "name": "Doc A Updated",
        "description": "Updated description",
        "document_type": "text",
        "file": (io.BytesIO(b"new content"), "updated.txt"),
    }
    response = client.put(
        f"/documents/{response.json['id']}",
        data=update_payload,
        headers=auth_headers,
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert response.json["name"] == update_payload["name"]
    assert response.json["description"] == update_payload["description"]
    assert response.json["document_type"] == update_payload["document_type"]
    assert response.json["original_filename"] == "updated.txt"
    assert response.json["content_type"] == "text/plain"
    assert response.json["storage_key"] != original_key

    updated = Document.query.session.get(Document, response.json["id"])
    assert updated is not None
    assert updated.storage_key == response.json["storage_key"]


def test_update_document_rejects_unsupported_extension(client, auth_headers):
    document = DocumentFactory()
    response = client.put(
        f"/documents/{document.id}",
        data={"file": (io.BytesIO(b"bin"), "document.exe")},
        headers=auth_headers,
        content_type="multipart/form-data",
    )
    assert response.status_code == 422
    assert response.json["message"] == "unsupported file type"
