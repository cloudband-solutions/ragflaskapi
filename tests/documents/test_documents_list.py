from tests.factories import DocumentFactory


def test_list_documents(client, auth_headers):
    DocumentFactory.create_batch(2)
    response = client.get("/documents", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json["records"]) == 2
