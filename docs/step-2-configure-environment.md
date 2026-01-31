# 2) Configure the environment

## 2.1 Create a virtual environment and install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2.2 Set environment variables
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
