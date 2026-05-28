"""Add duration_ms to research_logs

Revision ID: 20260528_030
Revises: 20260528_020
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa

revision = "20260528_030"
down_revision = "20260528_020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("research_logs", sa.Column("duration_ms", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("research_logs", "duration_ms")
