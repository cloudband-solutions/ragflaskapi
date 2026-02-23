# Cloning and project naming

## Copy the repository
```bash
cp -R /home/ralampay/workspace/cloudband/default_api_flask /home/ralampay/workspace/cloudband/ragapi
cd /home/ralampay/workspace/cloudband/ragapi
```

## Update the project naming defaults
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
