from pathlib import Path
import io
import os

import click
from flask import current_app
from flask.cli import with_appcontext
from flask_migrate.cli import db as db_cli
from openai import OpenAI
from pypdf import PdfReader
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
import tiktoken

from app import db
from app.helpers.api_helpers import build_password_hash
from app.models.document import Document
from app.models.document_embedding import DocumentEmbedding
from app.models.user import User
from app.storage import get_storage


DEFAULT_CHUNK_TOKENS = 800
DEFAULT_CHUNK_OVERLAP = 100
DEFAULT_BATCH_SIZE = 50


def register_cli(app):
    @app.cli.group()
    def system():
        """System tasks."""
        pass

    @system.command("greet")
    def greet():
        """Print hello world."""
        click.echo("hello world")

    @system.command("create-admin")
    @click.option("--email", default="admin@example.com", show_default=True)
    @click.option("--password", default="password", show_default=True)
    @click.option("--first-name", default="Test", show_default=True)
    @click.option("--last-name", default="Admin", show_default=True)
    @click.option(
        "--force",
        is_flag=True,
        help="Update existing user if the email already exists.",
    )
    @with_appcontext
    def create_admin(email, password, first_name, last_name, force):
        """Create a default admin user."""
        user = User.query.filter_by(email=email).first()
        if user is not None and not force:
            click.echo("Admin user already exists. Use --force to update it.")
            return

        if user is None:
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password_hash=build_password_hash(password),
                status="active",
            )
            db.session.add(user)
            db.session.commit()
            click.echo("Admin user created.")
            return

        user.first_name = first_name
        user.last_name = last_name
        user.password_hash = build_password_hash(password)
        user.status = "active"
        db.session.commit()
        click.echo("Admin user updated.")

    @system.command("openai-embed-document")
    @click.option("--document-id", required=True)
    @click.option("--chunk-size", default=DEFAULT_CHUNK_TOKENS, show_default=True, type=int)
    @click.option(
        "--chunk-overlap", default=DEFAULT_CHUNK_OVERLAP, show_default=True, type=int
    )
    @with_appcontext
    def openai_embed_document(document_id, chunk_size, chunk_overlap):
        """Embed a document from storage and save vectors."""
        use_openai = current_app.config.get("USE_OPENAI", "true")
        if str(use_openai).lower() not in {"1", "true", "yes", "y"}:
            raise click.ClickException("USE_OPENAI is disabled; no embedder available.")

        if chunk_size <= 0:
            raise click.ClickException("--chunk-size must be greater than 0.")
        if chunk_overlap < 0:
            raise click.ClickException("--chunk-overlap must be 0 or greater.")
        if chunk_overlap >= chunk_size:
            raise click.ClickException("--chunk-overlap must be less than --chunk-size.")

        api_key = current_app.config.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        model = current_app.config.get("OPENAI_EMBEDDING_MODEL") or os.getenv(
            "OPENAI_EMBEDDING_MODEL"
        )
        if not api_key:
            raise click.ClickException("OPENAI_API_KEY is required.")
        if not model:
            raise click.ClickException("OPENAI_EMBEDDING_MODEL is required.")

        document = db.session.get(Document, document_id)
        if document is None:
            raise click.ClickException("Document not found.")

        click.echo(f"Downloading document {document.id}...")
        data = get_storage().read(document.storage_key)
        text_content = _extract_text(document, data)
        if not text_content.strip():
            raise click.ClickException("No text content extracted from document.")

        encoding = _encoding_for_model(model)
        tokens = encoding.encode(text_content)
        chunks = _chunk_tokens(encoding, tokens, chunk_size, chunk_overlap)

        click.echo(f"Total tokens: {len(tokens)}")
        click.echo(f"Expected chunks: {len(chunks)}")

        existing = (
            DocumentEmbedding.query.filter_by(document_id=document.id)
            .delete(synchronize_session=False)
        )
        if existing:
            click.echo(f"Removed existing embeddings: {existing}")

        client = OpenAI(api_key=api_key)
        created = 0
        batch = []

        with click.progressbar(chunks, label="Embedding chunks") as chunk_iter:
            for idx, chunk in enumerate(chunk_iter):
                response = client.embeddings.create(model=model, input=chunk)
                embedding = response.data[0].embedding

                batch.append(
                    DocumentEmbedding(
                        document_id=document.id,
                        document_type=document.document_type,
                        embedding=embedding,
                        chunk_index=idx,
                        content=chunk,
                    )
                )
                created += 1

                if len(batch) >= DEFAULT_BATCH_SIZE:
                    db.session.add_all(batch)
                    db.session.commit()
                    batch = []

        if batch:
            db.session.add_all(batch)
            db.session.commit()

        click.echo(f"Rows produced: {created}")


def _quote_identifier(name):
    return f"\"{name.replace('\"', '\"\"')}\""


def _ensure_sqlite_db(database_path):
    if not database_path or database_path == ":memory:":
        click.echo("SQLite in-memory database does not need creation.")
        return
    path = Path(database_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{path}")
    engine.connect().close()
    click.echo(f"SQLite database ready at {path}")


@db_cli.command("create")
@with_appcontext
def create_db():
    """Create the configured database if it does not exist."""
    database_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI")
    if not database_uri:
        raise click.ClickException("SQLALCHEMY_DATABASE_URI is not configured.")

    url = make_url(database_uri)
    if url.get_backend_name() == "sqlite":
        _ensure_sqlite_db(url.database)
        return

    db_name = url.database
    if not db_name:
        raise click.ClickException("Database name is missing from SQLALCHEMY_DATABASE_URI.")

    try:
        admin_url = url.set(database="postgres")
    except AttributeError:
        admin_url = url._replace(database="postgres")

    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as connection:
        exists = connection.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": db_name},
        ).scalar()
        if exists:
            click.echo(f"Database already exists: {db_name}")
            return
        connection.execute(text(f"CREATE DATABASE {_quote_identifier(db_name)}"))
        click.echo(f"Database created: {db_name}")


def _extract_text(document, data):
    filename = (document.original_filename or "").lower()
    content_type = (document.content_type or "").lower()
    is_pdf = content_type == "application/pdf" or filename.endswith(".pdf") or data[:4] == b"%PDF"

    if is_pdf:
        reader = PdfReader(io.BytesIO(data))
        parts = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(parts)

    return data.decode("utf-8", errors="ignore")


def _encoding_for_model(model):
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def _chunk_tokens(encoding, tokens, chunk_size, chunk_overlap):
    if not tokens:
        return []
    step = max(chunk_size - chunk_overlap, 1)
    return [
        encoding.decode(tokens[i : i + chunk_size])
        for i in range(0, len(tokens), step)
    ]
