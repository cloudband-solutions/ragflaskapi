# Default Flask API

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
export FLASK_APP=wsgi.py
flask run
```

## Run with Gunicorn

```bash
gunicorn wsgi:app
```

## Database commands (Flask-Migrate)

```bash
export FLASK_APP=wsgi.py
flask db init
flask db migrate -m "init"
flask db upgrade
```

## Tests
```bash
pytest
```
Tests are organized by domain under `tests/` (for example `tests/system/` and
`tests/users/`), with separate files for each CRUD operation.

## Creating a New Model

1. Defining a new model with fields
   - Add a new file in `app/models/` (e.g. `app/models/project.py`).
   - Define a SQLAlchemy model using the shared `db` instance:
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
   - Export the model in `app/models/__init__.py` (follow the `User` pattern).

2. Migrating changes to the database
   - Generate and apply a migration with Flask-Migrate:
     ```bash
     export FLASK_APP=wsgi.py
     flask db migrate -m "add project model"
     flask db upgrade
     ```

3. Creating a factory for mocking
   - Add a factory in `tests/factories.py` using `factory_boy`:
     ```python
     class ProjectFactory(factory.alchemy.SQLAlchemyModelFactory):
         class Meta:
             model = Project
             sqlalchemy_session = db.session
             sqlalchemy_session_persistence = "commit"

         name = factory.Sequence(lambda n: f"Project {n}")
     ```

4. Testing
   - Add tests under the domain folders in `tests/` using pytest, similar to
     `tests/users/test_create.py`.
   - Use the factory to create records in tests (e.g. `ProjectFactory()` or
     `ProjectFactory.create_batch(2)`), and exercise any new routes or operations.

## Creating a Controller for a Model
1. Define tests
   - Create tests in the domain folders (e.g. `tests/projects/`) for the new endpoints,
     following `tests/users/test_create.py`.
   - Use the model factory to seed records and cover list/show/create/update/delete.
   - Example test file (e.g. `tests/projects/test_create.py`):

     ```python
     from app.models.project import Project
     from tests.factories import ProjectFactory


     def test_list_projects(client, auth_headers):
         ProjectFactory.create_batch(2)
         response = client.get("/api/projects", headers=auth_headers)
         assert response.status_code == 200
         assert len(response.json["records"]) == 2


     def test_show_project(client, auth_headers):
         project = ProjectFactory()
         response = client.get(f"/api/projects/{project.id}", headers=auth_headers)
         assert response.status_code == 200
         assert response.json["id"] == project.id


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


     def test_update_project_valid(client, auth_headers):
         project = ProjectFactory()
         payload = {"name": "Updated"}
         response = client.put(
             f"/api/projects/{project.id}", json=payload, headers=auth_headers
         )
         assert response.status_code == 200
         assert response.json["name"] == payload["name"]


     def test_delete_project(client, auth_headers):
         project = ProjectFactory()
         response = client.delete(f"/api/projects/{project.id}", headers=auth_headers)
         assert response.status_code == 200
         assert response.json == {"message": "ok"}
     ```

2. Define the controller
   - Add a controller module in `app/controllers/` (e.g. `app/controllers/projects_controller.py`).
   - Follow the `users_controller` pattern: use `flask` request/jsonify helpers,
     optional auth decorators from `app/controllers/authenticated_controller.py`,
     and fetch models via SQLAlchemy queries.
   - Register routes in `app/routes.py` using `api_bp.add_url_rule`.
   - Example controller:
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
   - Example route wiring in `app/routes.py`:
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

3. CRUD implementations
   - Implement `index`, `show`, `create`, `update`, `delete` functions in the controller.
   - For create/update, follow the `app/operations` pattern (see
     `app/operations/users/save.py`) for validation and persistence.
   - For delete, follow the model behavior (e.g. soft delete like `User.soft_delete()`),
     then return a simple JSON response (`{"message": "ok"}`).
   - Example operation skeleton (e.g. `app/operations/projects/save.py`):
     ```python
     from app import db
     from app.operations.validator import Validator
     from app.models.project import Project


     class Save(Validator):
         def __init__(self, project=None, name=None):
             self.project = project
             self.name = name
             super().__init__()

         def execute(self):
             self.validate()
             if not self.valid():
                 return

             if self.project is None:
                 self.project = Project()
                 db.session.add(self.project)

             self.project.name = self.name
             db.session.commit()

         def validate(self):
             if not self.name:
                 self.add_error("name", "required")
     ```
