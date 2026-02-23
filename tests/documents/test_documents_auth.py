from tests.factories import DocumentFactory


def test_documents_public_when_auth_disabled(client):
    response = client.get("/documents")
    assert response.status_code == 200


def test_documents_requires_auth_when_enabled(app, client):
    app.config["AUTHENTICATE_PUBLIC_DOCUMENTS"] = "true"

    response = client.get("/documents")
    assert response.status_code == 403


def test_documents_allows_auth_when_enabled(app, client, auth_headers):
    app.config["AUTHENTICATE_PUBLIC_DOCUMENTS"] = "true"

    response = client.get("/documents", headers=auth_headers)
    assert response.status_code == 200


def test_documents_allows_non_admin_get_index(client, user_headers):
    response = client.get("/documents", headers=user_headers)
    assert response.status_code == 200


def test_documents_allows_non_admin_get_show(client, user_headers):
    document = DocumentFactory()
    response = client.get(f"/documents/{document.id}", headers=user_headers)
    assert response.status_code == 200


def test_documents_requires_admin_for_create(client, user_headers):
    response = client.post("/documents", data={}, headers=user_headers)
    assert response.status_code == 403


def test_documents_requires_admin_for_update(client, user_headers):
    document = DocumentFactory()
    response = client.put(
        f"/documents/{document.id}",
        json={"name": "Updated"},
        headers=user_headers,
    )
    assert response.status_code == 403


def test_documents_requires_admin_for_delete(client, user_headers):
    document = DocumentFactory()
    response = client.delete(f"/documents/{document.id}", headers=user_headers)
    assert response.status_code == 403


def test_documents_requires_admin_for_enqueue(client, user_headers):
    document = DocumentFactory(embedding_status="failed")
    response = client.post(
        f"/documents/{document.id}/enqueue",
        headers=user_headers,
    )
    assert response.status_code == 403
