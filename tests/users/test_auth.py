
def test_requires_auth(client):
    response = client.get("/api/users")
    assert response.status_code == 403
