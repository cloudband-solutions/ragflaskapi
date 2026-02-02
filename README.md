# RAG Flask API

A Retrieval Augmented Generation engine in Flask.

## Dev Setup

0. (Optional) Create your python environment and install packages.

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

1. Create `.env` file and modify values accordingly.

```bash
cp .env.example .env
```

Test-only overrides:
- If `FLASK_ENV=test`, the app will also load `.env.test` (and override values).
- Use this for LocalStack credentials/endpoint and test bucket configuration.

Storage settings:
- Test, development, and production use Amazon S3 via the AWS variables below.
- Test should point `AWS_S3_ENDPOINT` to LocalStack (e.g., `http://localhost:4566`).

Required environment variables for S3:
- `AWS_S3_BUCKET`
- `AWS_REGION`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- Optional: `AWS_S3_ENDPOINT` (S3-compatible endpoints)
- Optional: `AWS_S3_PREFIX` (key prefix inside the bucket)

## PostgreSQL (Docker)

Use a local PostgreSQL container and point the app at it via `DB_*` or `DATABASE_URL`.

1. Start a Postgres container:

```bash
docker run --name ragflaskapi-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=ragflaskapi_development \
  -p 5432:5432 \
  -d postgres:15
```

2. Update `.env` to match the container:

```bash
DB_NAME=ragflaskapi
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

This maps to `database.yaml` and becomes:
`postgresql+psycopg2://postgres:postgres@localhost:5432/ragflaskapi_development`.

Optional: use a full URI instead of components:

```bash
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ragflaskapi_development
```

LocalStack setup for tests:
1. Run LocalStack with S3 enabled (defaults to `http://localhost:4566`).
2. Export test env vars (example values):
   - `AWS_S3_ENDPOINT=http://localhost:4566`
   - `AWS_S3_BUCKET=ragflaskapi-test`
   - `AWS_REGION=us-east-1`
   - `AWS_ACCESS_KEY_ID=test`
   - `AWS_SECRET_ACCESS_KEY=test`
3. Create the test bucket in LocalStack (example):
   - `aws --endpoint-url http://localhost:4566 s3 mb s3://ragflaskapi-test`
   - Or use `S3_BUCKET_NAME=ragflaskapi-test ./bin/create_dev_s3_bucket.sh`

2. Initialize the database

```bash
flask db create
flask db init
flask db migrate -m "init"
flask db upgrade
```

2. Run tests:

```bash
./bin/test
```

3. Run the server:

```bash
./bin/dev
```

## Docker Compose (foreground)

Build and run the API + Postgres in the foreground (no `-d`):

```bash
docker-compose up --build
```

Stop everything with `Ctrl+C`. If you need to initialize the database inside the
container, run:

```bash
docker-compose exec api flask db upgrade
```

To use a specific env file and keep the container in the foreground:

```bash
docker compose --env-file .env up --build
```

The API container runs Gunicorn directly (no `bin/dev`) via the container command.

## One-off DB tasks (ephemeral container)

If you want to run migrations or database setup in a server setting where the
container is removed after the command finishes, use `docker compose run --rm`:

```bash
docker compose --env-file .env run --rm api flask db upgrade
```

To create and apply new migrations:

```bash
docker compose --env-file .env run --rm api flask db migrate -m "your message"
docker compose --env-file .env run --rm api flask db upgrade
```

If you need to initialize Alembic metadata in a fresh environment:

```bash
docker compose --env-file .env run --rm api flask db init
```

To create the default admin user in an ephemeral container:

```bash
docker compose --env-file .env run --rm api flask system create-admin
```

Re-run with `--force` to update the user/password:

```bash
docker compose --env-file .env run --rm api flask system create-admin --force
```
