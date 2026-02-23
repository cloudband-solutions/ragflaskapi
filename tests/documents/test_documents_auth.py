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
