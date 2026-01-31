def test_requires_auth(client):
    response = client.get("/documents")
    assert response.status_code == 403
