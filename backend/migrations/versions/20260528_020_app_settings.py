"""Add app_settings table — v0.1.1

Revision ID: 20260528_020
Revises: 20260527_010
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa

revision = "20260528_020"
down_revision = "20260527_010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(128), primary_key=True, nullable=False),
        sa.Column("value", sa.Text, nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("app_settings")
