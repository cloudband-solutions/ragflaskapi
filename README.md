# Flask API Starter

This repository is a minimal Flask API scaffold. This tutorial shows how to
replicate it into a new project named `ragapi`, configure it, and extend it with
new models and controllers.

## 1) Create a new project from this codebase

### 1.1 Copy the repository
```bash
cp -R /home/ralampay/workspace/cloudband/default_api_flask /home/ralampay/workspace/cloudband/ragapi
cd /home/ralampay/workspace/cloudband/ragapi
```

### 1.2 Update the project naming defaults
Search and replace the default name with your new one:
```bash
rg -n "default_flask_api|default-flask-api|Default Flask API"
```

Update these files (recommended):
- `README.md` (title and any references)
- `config.py` (default DB URI and SECRET_KEY)
- `tests/settings.py` (test DB URI)

Suggested defaults:
- `default_flask_api` -> `ragapi`
- `default-flask-api-secret` -> `ragapi-secret`

Example edits:
```python
# config.py
SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    _db_config.get("uri", "postgresql+psycopg2://localhost:5432/ragapi"),
)
SECRET_KEY = os.getenv("SECRET_KEY", "ragapi-secret")
```

```python
# tests/settings.py
SQLALCHEMY_DATABASE_URI = _db_config.get(
    "uri", "postgresql+psycopg2://localhost:5432/ragapi_test"
)
```

## 2) Configure the environment

### 2.1 Create a virtual environment and install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2.2 Set environment variables
You can export these in your shell or place them in a `.env` file.

```bash
export FLASK_APP=wsgi.py
export FLASK_ENV=development
export SECRET_KEY="ragapi-secret"
export DB_USERNAME=...
export DB_PASSWORD=...
export DB_HOST=...
export DB_PORT=...
export DB_NAME=ragapi
```

The database config in `database.yaml` uses these environment variables:
```yaml
development:
  uri: postgresql+psycopg2://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}_development
test:
  uri: postgresql+psycopg2://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}_test
production:
  uri: postgresql+psycopg2://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
```

## 3) Run the server
```bash
flask run
```

## 4) Run with Gunicorn
```bash
gunicorn wsgi:app
```

## 5) Database migrations (Flask-Migrate)
```bash
export FLASK_APP=wsgi.py
flask db init
flask db migrate -m "init"
flask db upgrade
```

## 6) Tests
```bash
pytest
```
Tests are organized by domain under `tests/` (for example `tests/system/` and
`tests/users/`), with separate files for each CRUD operation.

## 7) Command-line routines (Flask CLI)
This project uses Flask's built-in CLI, which is powered by the `click` library.
Custom commands live in `app/cli.py` and are registered in `app/__init__.py`
via `register_cli(app)` inside `create_app`.

### 7.1 Run a command
```bash
flask --app wsgi.py system greet
```

### 7.2 Template for new commands
Add a command group and subcommand in `app/cli.py`:
```python
import click


def register_cli(app):
    @app.cli.group()
    def system():
        """System tasks."""
        pass

    @system.command("greet")
    def greet():
        """Print hello world."""
        click.echo("hello world")
```

Wire it in `app/__init__.py`:
```python
from app.cli import register_cli

register_cli(app)
```

### 7.3 About `click`

`click` is a Python library for building composable command-line interfaces. It
provides decorators for commands and groups, automatic help text generation,
argument and option parsing, and utility functions like `click.echo` for
console output. Flask uses `click` under the hood, so any `@app.cli.command()`
or `@app.cli.group()` you define becomes a first-class Flask CLI command.

## 8) Create a new model (example: Project)

### 8.1 Define the model
Create `app/models/project.py`:
```python
from datetime import datetime
from uuid import uuid4

from app import db


class Project(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
```

Export the model in `app/models/__init__.py` following the `User` pattern.

### 8.2 Add a factory for tests
Update `tests/factories.py`:
```python
class ProjectFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Project
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Project {n}")
```

### 8.3 Create the migration
```bash
export FLASK_APP=wsgi.py
flask db migrate -m "add project model"
flask db upgrade
```

## 9) Create a controller (example: Project)

### 9.1 Add tests (domain + per-operation files)
Create a domain folder under `tests/` (for example `tests/projects/`), and split
each CRUD operation into its own file (similar to `tests/users/test_create.py`).

Example files:
- `tests/projects/test_list.py`
- `tests/projects/test_show.py`
- `tests/projects/test_create.py`
- `tests/projects/test_update.py`
- `tests/projects/test_delete.py`

Example stubs:

`tests/projects/test_list.py`
```python
from tests.factories import ProjectFactory


def test_list_projects(client, auth_headers):
    ProjectFactory.create_batch(2)
    response = client.get("/api/projects", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json["records"]) == 2
```

`tests/projects/test_show.py`
```python
from tests.factories import ProjectFactory


def test_show_project(client, auth_headers):
    project = ProjectFactory()
    response = client.get(f"/api/projects/{project.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json["id"] == project.id
```

`tests/projects/test_create.py`
```python
from app.models.project import Project
from tests.factories import ProjectFactory


def test_create_project_invalid(client, auth_headers):
    response = client.post("/api/projects", json={}, headers=auth_headers)
    assert response.status_code == 422
    assert response.json["name"] == ["required"]


def test_create_project_valid(client, auth_headers):
    payload = {"name": "Alpha"}
    response = client.post("/api/projects", json=payload, headers=auth_headers)
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
        f"/api/projects/{project.id}", json=payload, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json["name"] == payload["name"]
```

`tests/projects/test_delete.py`
```python
from tests.factories import ProjectFactory


def test_delete_project(client, auth_headers):
    project = ProjectFactory()
    response = client.delete(f"/api/projects/{project.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json == {"message": "ok"}
```

### 8.2 Add the controller
Create `app/controllers/projects_controller.py`:
```python
from flask import jsonify, request

from app import db
from app.controllers.authenticated_controller import authenticate_user, authorize_active
from app.models.project import Project
from app.operations.projects.save import Save as SaveProject


def _get_payload():
    data = request.get_json(silent=True)
    if data is not None:
        return data
    if request.form:
        return request.form
    return {}


@authenticate_user
@authorize_active
def index():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return jsonify({"records": [project.to_dict() for project in projects]})


@authenticate_user
@authorize_active
def show(project_id):
    project = Project.query.get(project_id)
    if project is None:
        return jsonify({"message": "not found"}), 404
    return jsonify(project.to_dict())


@authenticate_user
@authorize_active
def create():
    payload = _get_payload()
    cmd = SaveProject(name=payload.get("name"))
    cmd.execute()

    if cmd.valid():
        return jsonify(cmd.project.to_dict())
    return jsonify(cmd.payload), 422


@authenticate_user
@authorize_active
def update(project_id):
    project = Project.query.get(project_id)
    if project is None:
        return jsonify({"message": "not found"}), 404

    payload = _get_payload()
    cmd = SaveProject(project=project, name=payload.get("name"))
    cmd.execute()

    if cmd.valid():
        return jsonify(cmd.project.to_dict())
    return jsonify(cmd.payload), 422


@authenticate_user
@authorize_active
def delete(project_id):
    project = Project.query.get(project_id)
    if project is None:
        return jsonify({"message": "not found"}), 404

    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "ok"})
```

### 8.3 Wire the routes
Update `app/routes.py`:
```python
from app.controllers.projects_controller import (
    create as create_project,
    delete as delete_project,
    index as list_projects,
    show as show_project,
    update as update_project,
)

api_bp.add_url_rule("/projects", view_func=list_projects, methods=["GET"])
api_bp.add_url_rule("/projects", view_func=create_project, methods=["POST"])
api_bp.add_url_rule(
    "/projects/<string:project_id>", view_func=show_project, methods=["GET"]
)
api_bp.add_url_rule(
    "/projects/<string:project_id>", view_func=update_project, methods=["PUT"]
)
api_bp.add_url_rule(
    "/projects/<string:project_id>", view_func=delete_project, methods=["DELETE"]
)
```

### 8.4 Add the operation (validation + persistence)
Create `app/operations/projects/save.py`:
```python
from app import db
from app.operations.validator import Validator
from app.models.project import Project


class Save(Validator):
    def __init__(self, project=None, name=None):
        super().__init__()
        self.project = project
        self.name = name
        self.payload = {"name": []}

    def execute(self):
        self._validate()
        if not self.valid():
            return

        if self.project is None:
            self.project = Project()
            db.session.add(self.project)

        self.project.name = self.name
        db.session.commit()

    def _validate(self):
        if not self.name:
            self.payload["name"].append("required")
        self.count_errors()
```
