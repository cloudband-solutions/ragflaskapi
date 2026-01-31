"""add pgvector extension

Revision ID: 9b3c7f4d2a1e
Revises: 435225f78720
Create Date: 2026-01-31 23:12:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '9b3c7f4d2a1e'
down_revision = '435225f78720'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')


def downgrade():
    op.execute('DROP EXTENSION IF EXISTS vector')
