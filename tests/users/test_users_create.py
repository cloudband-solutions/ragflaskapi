from app.models.user import User


def test_create_user_invalid(client, auth_headers):
    response = client.post("/users", json={}, headers=auth_headers)
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
    response = client.post("/users", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json["email"] == payload["email"]
    created = User.query.filter_by(email=payload["email"]).first()
    assert created is not None
    assert created.password_hash != payload["password"]
