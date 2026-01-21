from app.models.user import User
from tests.factories import UserFactory


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_list_users(client, auth_headers):
    UserFactory.create_batch(2)
    response = client.get("/api/users", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json["records"]) == 2


def test_show_user(client, auth_headers):
    user = UserFactory()
    response = client.get(f"/api/users/{user.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json["id"] == user.id


def test_create_user_invalid(client, auth_headers):
    response = client.post("/api/users", json={}, headers=auth_headers)
    assert response.status_code == 422
    assert response.json["email"] == ["required"]
    assert response.json["first_name"] == ["required"]
    assert response.json["last_name"] == ["required"]
    assert response.json["password"] == ["required"]
    assert response.json["password_confirmation"] == ["required"]


def test_create_user_valid(client, auth_headers):
    payload = {
        "email": "person@example.com",
        "first_name": "Taylor",
        "last_name": "Reed",
        "password": "password",
        "password_confirmation": "password",
    }
    response = client.post("/api/users", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json["email"] == payload["email"]
    created = User.query.filter_by(email=payload["email"]).first()
    assert created is not None
    assert created.password_hash != payload["password"]


def test_update_user_valid(client, auth_headers):
    user = UserFactory()
    payload = {
        "email": "updated@example.com",
        "first_name": "Updated",
        "last_name": "Name",
    }
    response = client.put(f"/api/users/{user.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json["email"] == payload["email"]


def test_update_user_unique_email(client, auth_headers):
    user = UserFactory(email="first@example.com")
    other_user = UserFactory(email="second@example.com")
    payload = {"email": user.email}
    response = client.put(
        f"/api/users/{other_user.id}", json=payload, headers=auth_headers
    )
    assert response.status_code == 422
    assert response.json["email"] == ["already taken"]


def test_delete_user(client, auth_headers):
    user = UserFactory()
    response = client.delete(f"/api/users/{user.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json == {"message": "ok"}


def test_requires_auth(client):
    response = client.get("/api/users")
    assert response.status_code == 403
