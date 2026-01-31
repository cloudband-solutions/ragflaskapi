from tests.factories import DocumentFactory


def test_show_document(client, auth_headers):
    document = DocumentFactory()
    response = client.get(f"/documents/{document.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json["id"] == document.id
