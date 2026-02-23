"""add document embedding status

Revision ID: 6d0a6f7c1d47
Revises: 2088930d2e5d
Create Date: 2026-02-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "6d0a6f7c1d47"
down_revision = "2088930d2e5d"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("documents", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("embedding_status", sa.String(length=32), nullable=False, server_default="pending")
        )
        batch_op.add_column(sa.Column("enqueue_error", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("embedding_error", sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table("documents", schema=None) as batch_op:
        batch_op.drop_column("embedding_error")
        batch_op.drop_column("enqueue_error")
        batch_op.drop_column("embedding_status")
