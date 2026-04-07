from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0001_create_users_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("member", "admin", name="user_role"),
            nullable=False,
            server_default="member",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_name", "users", ["name"])


def downgrade() -> None:
    op.drop_index("ix_users_name", table_name="users")
    op.drop_table("users")
    sa.Enum("member", "admin", name="user_role").drop(op.get_bind(), checkfirst=True)
