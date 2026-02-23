# Environment and dotenv configuration

## Create a virtual environment and install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configure dotenv (.env)
This project uses `python-dotenv`. Variables in `.env` (and `.flaskenv` if you
choose to add one) are loaded automatically when the app starts.

Copy the example file and update the values:
```bash
cp .env.example .env
```

Test-only overrides:
- If `FLASK_ENV=test`, the app will also load `.env.test` (and override values).
- Use this for LocalStack credentials/endpoint and test bucket configuration.

Example `.env`:
```bash
FLASK_APP=wsgi.py
FLASK_ENV=development
SECRET_KEY="ragapi-secret"
DB_USERNAME=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=...
DB_NAME=ragapi
# Optional full URI override:
# DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/ragapi_development
AWS_S3_BUCKET=...
AWS_REGION=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
# Optional S3-compatible endpoint (e.g. localstack):
AWS_S3_ENDPOINT=
# Optional prefix inside the bucket:
AWS_S3_PREFIX=
AUTHENTICATE_PUBLIC_DOCUMENTS=false
# SQS embedding worker
SQS_QUEUE_URL=
# Optional SQS endpoint (e.g. localstack):
AWS_SQS_ENDPOINT=
SQS_REGION=
# Local embedding model (GGUF)
LOCAL_EMBEDDING_MODEL_PATH=
LOCAL_EMBEDDING_N_CTX=2048
LOCAL_EMBEDDING_N_THREADS=4
LOCAL_EMBEDDING_N_BATCH=64
# OpenAI embeddings
OPENAI_API_KEY=
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
USE_OPENAI=true
```

Storage adapter selection:
- Test, development, and production use Amazon S3 via the AWS variables above.
- In test, set `AWS_S3_ENDPOINT` to a LocalStack endpoint (e.g., `http://localhost:4566`).

Document access:
- Set `AUTHENTICATE_PUBLIC_DOCUMENTS=true` to require auth for `GET /documents`.

Embedding queue:
- Documents enqueue embedding jobs to SQS. Ensure `SQS_QUEUE_URL` is configured.

If you prefer to keep Flask CLI variables separate, move `FLASK_APP` and
`FLASK_ENV` into a `.flaskenv` file instead; it will be loaded as well.

The database config in `database.yaml` uses these environment variables:
```yaml
development:
  uri: postgresql+psycopg2://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}_development
test:
  uri: postgresql+psycopg2://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}_test
production:
  uri: postgresql+psycopg2://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
```
