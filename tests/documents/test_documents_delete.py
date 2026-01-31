from tests.factories import DocumentFactory


def test_delete_document(client, auth_headers, app):
    document = DocumentFactory()
    storage = app.extensions["storage"]
    storage.save(document.storage_key, b"payload", content_type="application/octet-stream")

    response = client.delete(f"/documents/{document.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json["message"] == "ok"
