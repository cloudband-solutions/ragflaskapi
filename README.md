# RAG Flask API

A Retrieval Augmented Generation API built with Flask.

## Quick start (local dev)

1) Create a virtualenv and install deps:

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

2) Create your environment file:

```bash
cp .env.example .env
```

3) Start Postgres (Docker):

```bash
docker run --name ragflaskapi-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=ragflaskapi_development \
  -p 5432:5432 \
  -d postgres:15
```

4) Point the app at the DB in `.env`:

```bash
DB_NAME=ragflaskapi
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

5) Initialize the database and run the server:

```bash
flask db create
flask db init
flask db migrate -m "init"
flask db upgrade

./bin/dev
```

## Essential configuration

Environment file:
- Base config lives in `.env`.
- If `FLASK_ENV=test`, `.env.test` is loaded and overrides values.

Storage (S3 or S3-compatible):
- Required: `AWS_S3_BUCKET`, `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Optional: `AWS_S3_ENDPOINT`, `AWS_S3_PREFIX`

Database:
- Use `DB_*` values or a full `DATABASE_URL`.
- The default mapping follows `database.yaml`.

OpenAI embeddings:
- Required: `OPENAI_API_KEY`
- Optional: `OPENAI_EMBEDDING_MODEL` (default `text-embedding-3-small`)
- Optional: `USE_OPENAI` (default `true`)

## Common workflows

Run tests:
```bash
./bin/test
```

Create an admin user:
```bash
flask --app wsgi.py system create-admin
```

Embed a document into `document_embeddings`:
```bash
flask --app wsgi.py system openai-embed-document --document-id <uuid>
```

## Docker Compose (foreground)

Run API + Postgres in the foreground:
```bash
docker-compose up --build
```

Initialize the DB inside the container:
```bash
docker-compose exec api flask db upgrade
```

Use a specific env file:
```bash
docker compose --env-file .env up --build
```

The API container runs Gunicorn directly (no `./bin/dev`).

Verify the container is healthy:
```bash
curl http://localhost:8000/health
```

## One-off DB tasks (ephemeral container)

Apply migrations:
```bash
docker compose --env-file .env run --rm api flask db upgrade
```

Create/apply migrations:
```bash
docker compose --env-file .env run --rm api flask db migrate -m "your message"
docker compose --env-file .env run --rm api flask db upgrade
```

Initialize Alembic metadata:
```bash
docker compose --env-file .env run --rm api flask db init
```

Create/update default admin user:
```bash
docker compose --env-file .env run --rm api flask system create-admin
docker compose --env-file .env run --rm api flask system create-admin --force
```

## Documentation

Start here: `docs/README.md`.
