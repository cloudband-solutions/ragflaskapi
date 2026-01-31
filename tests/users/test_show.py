from tests.factories import UserFactory


def test_show_user(client, auth_headers):
    user = UserFactory()
    response = client.get(f"/api/users/{user.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json["id"] == user.id
