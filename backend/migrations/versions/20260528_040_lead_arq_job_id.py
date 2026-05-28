"""Add arq_job_id to leads

Revision ID: 20260528_040
Revises: 20260528_030
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa

revision = "20260528_040"
down_revision = "20260528_030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("arq_job_id", sa.String(100), nullable=True))


def downgrade() -> None:
    op.drop_column("leads", "arq_job_id")
