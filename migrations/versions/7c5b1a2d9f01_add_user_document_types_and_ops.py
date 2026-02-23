"""add user document types and ops user type

Revision ID: 7c5b1a2d9f01
Revises: 1b9f2c7a4e6f
Create Date: 2026-02-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "7c5b1a2d9f01"
down_revision = "1b9f2c7a4e6f"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("document_types", sa.JSON(), nullable=True))
        batch_op.drop_constraint("ck_users_user_type", type_="check")
        batch_op.create_check_constraint(
            "ck_users_user_type", "user_type IN ('user', 'admin', 'ops')"
        )


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint("ck_users_user_type", type_="check")
        batch_op.create_check_constraint(
            "ck_users_user_type", "user_type IN ('user', 'admin')"
        )
        batch_op.drop_column("document_types")
