"""add user type to users

Revision ID: 1b9f2c7a4e6f
Revises: 6d0a6f7c1d47
Create Date: 2026-02-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "1b9f2c7a4e6f"
down_revision = "6d0a6f7c1d47"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("user_type", sa.String(length=50), nullable=False, server_default="user")
        )
        batch_op.create_check_constraint(
            "ck_users_user_type", "user_type IN ('user', 'admin')"
        )


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint("ck_users_user_type", type_="check")
        batch_op.drop_column("user_type")
