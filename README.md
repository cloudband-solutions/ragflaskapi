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
