# 5) Database migrations (Flask-Migrate)
```bash
export FLASK_APP=wsgi.py
flask db create
flask db init
flask db migrate -m "init"
flask db upgrade
```

`flask db create` will create the configured database if it does not exist. It
uses `SQLALCHEMY_DATABASE_URI` (or the `database.yaml` config) to determine the
target database. For SQLite, it creates the database file if needed.
