
def test_requires_auth(client):
    response = client.get("/users")
    assert response.status_code == 403
