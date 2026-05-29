"""Add address fields to leads (city, state, country, zip_code, street_address)

Revision ID: 20260529_060
Revises: 20260528_050
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa

revision = "20260529_060"
down_revision = "20260528_050"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("street_address", sa.Text(), nullable=True))
    op.add_column("leads", sa.Column("city",           sa.String(100), nullable=True))
    op.add_column("leads", sa.Column("state",          sa.String(100), nullable=True))
    op.add_column("leads", sa.Column("country",        sa.String(100), nullable=True))
    op.add_column("leads", sa.Column("zip_code",       sa.String(20),  nullable=True))


def downgrade() -> None:
    for col in ("street_address", "city", "state", "country", "zip_code"):
        op.drop_column("leads", col)
