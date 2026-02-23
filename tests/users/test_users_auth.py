
def test_requires_auth(client):
    response = client.get("/users")
    assert response.status_code == 403


def test_requires_admin_for_index(client, user_headers):
    response = client.get("/users", headers=user_headers)
    assert response.status_code == 403


def test_requires_admin_for_show(client, user_headers):
    response = client.get("/users/does-not-matter", headers=user_headers)
    assert response.status_code == 403


def test_requires_admin_for_create(client, user_headers):
    response = client.post("/users", json={}, headers=user_headers)
    assert response.status_code == 403


def test_requires_admin_for_update(client, user_headers):
    response = client.put("/users/does-not-matter", json={}, headers=user_headers)
    assert response.status_code == 403


def test_requires_admin_for_delete(client, user_headers):
    response = client.delete("/users/does-not-matter", headers=user_headers)
    assert response.status_code == 403
