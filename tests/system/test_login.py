from tests.factories import UserFactory


def test_login_success(client):
    user = UserFactory(email="login@example.com")
    response = client.post(
        "/api/login", json={"email": user.email, "password": "password"}
    )
    assert response.status_code == 200
    assert "token" in response.json


def test_login_invalid(client):
    response = client.post("/api/login", json={"email": "missing@example.com"})
    assert response.status_code == 422
    assert response.json["email"] == ["user not found"]
