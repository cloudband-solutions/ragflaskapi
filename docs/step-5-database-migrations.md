# 5) Database setup and migrations (Flask-Migrate)

## 5.1 Create the database
```bash
flask db create
```

## 5.2 Initialize migrations (first time only)
```bash
flask db init
```

## 5.3 Generate and apply migrations
```bash
flask db migrate -m "init"
flask db upgrade
```

`flask db create` will create the configured database if it does not exist. It
uses `SQLALCHEMY_DATABASE_URI` (or the `database.yaml` config) to determine the
target database. For SQLite, it creates the database file if needed.
