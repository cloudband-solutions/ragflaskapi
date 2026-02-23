def test_environment_requires_auth(client):
    response = client.get("/system/env")
    assert response.status_code == 403


def test_environment_returns_safe_values(app, client, auth_headers):
    app.config["AWS_REGION"] = "us-east-1"
    app.config["OPENAI_EMBEDDING_MODEL"] = "text-embedding-3-small"
    app.config["OPENAI_API_KEY"] = "should-not-leak"
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://secret"
    app.config["AWS_ACCESS_KEY_ID"] = "should-not-leak"

    response = client.get("/system/env", headers=auth_headers)
    assert response.status_code == 200

    payload = response.json["env"]
    assert payload["AWS_REGION"] == "us-east-1"
    assert payload["OPENAI_EMBEDDING_MODEL"] == "text-embedding-3-small"

    assert "OPENAI_API_KEY" not in payload
    assert "SQLALCHEMY_DATABASE_URI" not in payload
    assert "AWS_ACCESS_KEY_ID" not in payload
