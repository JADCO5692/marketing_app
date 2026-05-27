"""Initial schema — v0.1.0

Revision ID: 20260527_010
Revises:
Create Date: 2026-05-27
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260527_010"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # pgvector + uuid extensions (idempotent)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ── users ──────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("is_superuser", sa.Boolean(), default=False, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── companies ──────────────────────────────────────────────────────────────
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("domain", sa.String(255), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("sub_industry", sa.String(150), nullable=True),
        sa.Column("business_type", sa.String(50), nullable=True),
        sa.Column("company_size", sa.String(50), nullable=True),
        sa.Column("headcount_range", sa.String(50), nullable=True),
        sa.Column("revenue_range", sa.String(50), nullable=True),
        sa.Column("funding_stage", sa.String(50), nullable=True),
        sa.Column("years_operating", sa.Integer(), nullable=True),
        sa.Column("hiring_velocity", sa.String(20), nullable=True),
        sa.Column("region", sa.String(100), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("timezone", sa.String(60), nullable=True),
        sa.Column("tech_stack", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("pain_points", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("website_quality_score", sa.Float(), nullable=True),
        sa.Column("social_presence_score", sa.Float(), nullable=True),
        sa.Column("traffic_estimate", sa.String(50), nullable=True),
        sa.Column("recent_news", postgresql.JSONB(), nullable=True),
        sa.Column("research_status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("last_researched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_companies_domain", "companies", ["domain"], unique=True)
    op.create_index("ix_companies_industry", "companies", ["industry"])
    op.create_index("ix_companies_region", "companies", ["region"])
    op.create_index("ix_companies_funding_stage", "companies", ["funding_stage"])
    op.create_index("ix_companies_research_status", "companies", ["research_status"])

    # ── leads ──────────────────────────────────────────────────────────────────
    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("companies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("email_type", sa.String(50), nullable=True),
        sa.Column("email_deliverability", sa.String(50), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("linkedin_url", sa.Text(), nullable=True),
        sa.Column("job_title", sa.Text(), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("seniority_level", sa.String(50), nullable=True),
        sa.Column("is_decision_maker", sa.Boolean(), nullable=True),
        sa.Column("budget_authority", sa.Boolean(), nullable=True),
        sa.Column("icp_score", sa.Float(), nullable=True),
        sa.Column("intent_score", sa.Float(), nullable=True),
        sa.Column("engagement_readiness", sa.Float(), nullable=True),
        sa.Column("campaign_type_match", sa.String(50), nullable=True),
        sa.Column("personalization_tags", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("competitive_intel", postgresql.JSONB(), nullable=True),
        sa.Column("pain_point_clusters", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("raw_csv_data", postgresql.JSONB(), nullable=True),
        sa.Column("embedding", sa.Text(), nullable=True),  # stored as vector — see index below
        sa.Column("status", sa.String(30), nullable=False, server_default="raw"),
        sa.Column("duplicate_of", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_file", sa.Text(), nullable=True),
        sa.Column("source_row", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_leads_email", "leads", ["email"])
    op.create_index("ix_leads_phone", "leads", ["phone"])
    op.create_index("ix_leads_company_id", "leads", ["company_id"])
    op.create_index("ix_leads_status", "leads", ["status"])
    op.create_index("ix_leads_icp_score", "leads", ["icp_score"])

    # Convert the embedding column to vector type after table creation
    op.execute("ALTER TABLE leads ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536)")

    # ── research_logs ──────────────────────────────────────────────────────────
    op.create_table(
        "research_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("query", sa.Text(), nullable=True),
        sa.Column("raw_response", postgresql.JSONB(), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("cost_usd", sa.Float(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_research_logs_lead_id", "research_logs", ["lead_id"])
    op.create_index("ix_research_logs_source", "research_logs", ["source"])

    # ── segments ───────────────────────────────────────────────────────────────
    op.create_table(
        "segments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("filter_rules", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("lead_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_segments_name", "segments", ["name"], unique=True)

    # ── campaigns ──────────────────────────────────────────────────────────────
    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("segment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("segments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("subject_template", sa.Text(), nullable=True),
        sa.Column("body_template", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("open_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("click_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bounce_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("campaigns")
    op.drop_table("segments")
    op.drop_table("research_logs")
    op.drop_table("leads")
    op.drop_table("companies")
    op.drop_table("users")
