# Example test stubs

`tests/projects/test_list.py`
```python
from tests.factories import ProjectFactory


def test_list_projects(client, auth_headers):
    ProjectFactory.create_batch(2)
    response = client.get("/projects", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json["records"]) == 2
```

`tests/projects/test_show.py`
```python
from tests.factories import ProjectFactory


def test_show_project(client, auth_headers):
    project = ProjectFactory()
    response = client.get(f"/projects/{project.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json["id"] == project.id
```

`tests/projects/test_create.py`
```python
from app.models.project import Project
from tests.factories import ProjectFactory


def test_create_project_invalid(client, auth_headers):
    response = client.post("/projects", json={}, headers=auth_headers)
    assert response.status_code == 422
    assert response.json["name"] == ["required"]


def test_create_project_valid(client, auth_headers):
    payload = {"name": "Alpha"}
    response = client.post("/projects", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json["name"] == payload["name"]
    created = Project.query.filter_by(name=payload["name"]).first()
    assert created is not None
```

`tests/projects/test_update.py`
```python
from tests.factories import ProjectFactory


def test_update_project_valid(client, auth_headers):
    project = ProjectFactory()
    payload = {"name": "Updated"}
    response = client.put(
        f"/projects/{project.id}", json=payload, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json["name"] == payload["name"]
```

`tests/projects/test_delete.py`
```python
from tests.factories import ProjectFactory


def test_delete_project(client, auth_headers):
    project = ProjectFactory()
    response = client.delete(f"/projects/{project.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json == {"message": "ok"}
```
