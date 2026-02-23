# Controller example

## Add the controller
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

## Wire the routes
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

## Add the operation (validation + persistence)
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
