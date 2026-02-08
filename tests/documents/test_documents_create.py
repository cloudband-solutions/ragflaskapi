import io

from app.models.document import Document


def test_create_document_invalid(client, auth_headers):
    response = client.post("/documents", data={}, headers=auth_headers)
    assert response.status_code == 422
    assert response.json["message"] == "name is required"


def test_create_document_missing_file(client, auth_headers):
    response = client.post(
        "/documents", data={"name": "Doc 1"}, headers=auth_headers
    )
    assert response.status_code == 422
    assert response.json["message"] == "file is required"


def test_create_document_valid(client, auth_headers):
    payload = {
        "name": "Doc 1",
        "description": "First document",
        "document_type": "pdf",
        "file": (io.BytesIO(b"hello world"), "doc1.pdf"),
    }
    response = client.post(
        "/documents", data=payload, headers=auth_headers, content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert response.json["name"] == payload["name"]
    assert response.json["original_filename"] == "doc1.pdf"
    assert response.json["content_type"] == "application/pdf"
    assert response.json["storage_key"]
    assert len(response.json["storage_key"]) == 36

    created = Document.query.filter_by(name=payload["name"]).first()
    assert created is not None


def test_create_document_unique_name(client, auth_headers):
    payload = {
        "name": "Doc 1",
        "file": (io.BytesIO(b"one"), "doc1.txt"),
    }
    response = client.post(
        "/documents", data=payload, headers=auth_headers, content_type="multipart/form-data"
    )
    assert response.status_code == 200

    payload["file"] = (io.BytesIO(b"two"), "doc2.txt")
    response = client.post(
        "/documents", data=payload, headers=auth_headers, content_type="multipart/form-data"
    )
    assert response.status_code == 422
    assert response.json["message"] == "name must be unique"


def test_create_document_rejects_unsupported_extension(client, auth_headers):
    payload = {
        "name": "Doc 2",
        "file": (io.BytesIO(b"bin"), "doc2.exe"),
    }
    response = client.post(
        "/documents", data=payload, headers=auth_headers, content_type="multipart/form-data"
    )
    assert response.status_code == 422
    assert response.json["message"] == "unsupported file type"


def test_create_document_accepts_txt(client, auth_headers):
    payload = {
        "name": "Doc 3",
        "file": (io.BytesIO(b"text"), "doc3.txt"),
    }
    response = client.post(
        "/documents", data=payload, headers=auth_headers, content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert response.json["name"] == payload["name"]


def test_create_document_accepts_xlsx(client, auth_headers):
    payload = {
        "name": "Doc 4",
        "file": (io.BytesIO(b"excel"), "doc4.xlsx"),
    }
    response = client.post(
        "/documents", data=payload, headers=auth_headers, content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert response.json["name"] == payload["name"]


def test_create_document_accepts_pptx(client, auth_headers):
    payload = {
        "name": "Doc 5",
        "file": (io.BytesIO(b"ppt"), "doc5.pptx"),
    }
    response = client.post(
        "/documents", data=payload, headers=auth_headers, content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert response.json["name"] == payload["name"]
