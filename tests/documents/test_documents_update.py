from tests.factories import DocumentFactory


def test_update_document_valid(client, auth_headers):
    document = DocumentFactory()
    payload = {"name": "Updated name", "description": "Updated description"}
    response = client.put(
        f"/documents/{document.id}", json=payload, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json["name"] == payload["name"]
    assert response.json["description"] == payload["description"]


def test_update_document_unique_name(client, auth_headers):
    document = DocumentFactory(name="Doc 1")
    other = DocumentFactory(name="Doc 2")
    response = client.put(
        f"/documents/{other.id}", json={"name": document.name}, headers=auth_headers
    )
    assert response.status_code == 422
    assert response.json["message"] == "name must be unique"
