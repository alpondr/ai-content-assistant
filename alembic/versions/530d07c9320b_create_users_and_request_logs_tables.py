"""create users and request_logs tables

Revision ID: 530d07c9320b
Revises: 
Create Date: 2026-07-15 18:55:26.699404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '530d07c9320b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "request_logs",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("request_type", sa.String(), nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("output_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_request_logs_user_id", "request_logs", ["user_id"])
    op.create_index("ix_request_logs_created_at", "request_logs", ["created_at"])


def downgrade() -> None:
    # downgrade removes things in the reverse order they were created,
    # otherwise the foreign key on request_logs would block dropping users
    op.drop_index("ix_request_logs_created_at", table_name="request_logs")
    op.drop_index("ix_request_logs_user_id", table_name="request_logs")
    op.drop_table("request_logs")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
