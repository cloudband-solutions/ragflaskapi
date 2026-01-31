from tests.factories import UserFactory


def test_delete_user(client, auth_headers):
    user = UserFactory()
    response = client.delete(f"/users/{user.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json == {"message": "ok"}
