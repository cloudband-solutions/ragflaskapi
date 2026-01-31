# 8) Create a new model (example: Project)

## 8.1 Define the model
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

## 8.2 Add a factory for tests
Update `tests/factories.py`:
```python
class ProjectFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Project
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Project {n}")
```

## 8.3 Create the migration
```bash
export FLASK_APP=wsgi.py
flask db migrate -m "add project model"
flask db upgrade
```
