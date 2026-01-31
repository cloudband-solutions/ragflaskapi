from tests.factories import UserFactory


def test_list_users(client, auth_headers):
    UserFactory.create_batch(2)
    response = client.get("/users", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json["records"]) == 3
