# Command-line routines (Flask CLI)
This project uses Flask's built-in CLI, which is powered by the `click` library.
Custom commands live in `app/cli.py` and are registered in `app/__init__.py`
via `register_cli(app)` inside `create_app`.

## Run a command
```bash
flask --app wsgi.py system greet
```

## Embed a document with OpenAI
This command downloads a document from storage and writes embeddings into
`document_embeddings`.

```bash
flask --app wsgi.py system openai-embed-document --document-id <uuid>
```

Optional tuning flags (token-based):
```bash
flask --app wsgi.py system openai-embed-document \
  --document-id <uuid> \
  --chunk-size 800 \
  --chunk-overlap 100
```

Required environment variables:
- `OPENAI_API_KEY`
- `OPENAI_EMBEDDING_MODEL` (defaults to `text-embedding-3-small`)
- `USE_OPENAI` (defaults to `true`)

## Embed a document with a local GGUF model
This command uses `llama-cpp-python` with a `.gguf` model file.

```bash
flask --app wsgi.py system local-embed-document --document-id <uuid>
```

Required environment variables:
- `LOCAL_EMBEDDING_MODEL_PATH` (full path to a `.gguf` file)

Optional local tuning variables:
- `LOCAL_EMBEDDING_N_CTX` (default `2048`)
- `LOCAL_EMBEDDING_N_THREADS` (default `4`)
- `LOCAL_EMBEDDING_N_BATCH` (default `64`)

## Process SQS embedding jobs (continuous)
Runs as a long-lived process that polls SQS, downloads referenced S3 objects,
creates the `documents` record when needed, and writes embeddings. Press
`Ctrl+C` to stop.

```bash
flask --app wsgi.py system process-sqs-embedding --queue-url <sqs-url>
```

Optional flags:
- `--embedder auto|openai|local` (default `auto`)
- `--wait-time <seconds>` (default `10`)
- `--visibility-timeout <seconds>` (default `120`)
- `--delete-message/--no-delete-message` (default `--delete-message`)
- `--max-messages <count>` (default `1`, max `10`)
- `--chunk-size <tokens>` (default `800`)
- `--chunk-overlap <tokens>` (default `100`)

Required environment variables:
- `SQS_QUEUE_URL` (or pass `--queue-url`)
- `AWS_S3_BUCKET` (used to validate the payload bucket)
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

Optional SQS variables:
- `AWS_SQS_ENDPOINT` (for localstack)
- `SQS_REGION` (falls back to `AWS_REGION`)

Payload formats accepted:
- `{ "bucket": "my-bucket", "key": "path/to/file.pdf" }`
- `{ "document_id": "<uuid>", "name": "Title", "key": "path/to/file.pdf" }`
- S3 event payloads in `Records[0].s3.bucket.name` and `Records[0].s3.object.key`

If `--embedder auto` and `USE_OPENAI=true`, OpenAI will be used; otherwise the
local GGUF embedder will be used.

When processing a `document_id` payload, the worker updates `embedding_status`
to `processing`, then `embedded` on success or `failed` on error. Embedding
errors are stored in `embedding_error`.

Documents also track `enqueue_error` when a job could not be sent to SQS.

## Template for new commands
Add a command group and subcommand in `app/cli.py`:
```python
import click


def register_cli(app):
    @app.cli.group()
    def system():
        """System tasks."""
        pass

    @system.command("greet")
    def greet():
        """Print hello world."""
        click.echo("hello world")
```

Wire it in `app/__init__.py`:
```python
from app.cli import register_cli

register_cli(app)
```

## About `click`

`click` is a Python library for building composable command-line interfaces. It
provides decorators for commands and groups, automatic help text generation,
argument and option parsing, and utility functions like `click.echo` for
console output. Flask uses `click` under the hood, so any `@app.cli.command()`
or `@app.cli.group()` you define becomes a first-class Flask CLI command.
