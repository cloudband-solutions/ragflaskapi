from tests.factories import UserFactory


def test_update_user_valid(client, auth_headers):
    user = UserFactory()
    payload = {
        "email": "updated@example.com",
        "first_name": "Updated",
        "last_name": "Name",
    }
    response = client.put(f"/users/{user.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json["email"] == payload["email"]


def test_update_user_unique_email(client, auth_headers):
    user = UserFactory(email="first@example.com")
    other_user = UserFactory(email="second@example.com")
    payload = {"email": user.email}
    response = client.put(
        f"/users/{other_user.id}", json=payload, headers=auth_headers
    )
    assert response.status_code == 422
    assert response.json["email"] == ["already taken"]
