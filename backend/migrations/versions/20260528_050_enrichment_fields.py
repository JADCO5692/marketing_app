"""Add enrichment fields to leads and companies (v0.5.0)

Revision ID: 20260528_050
Revises: 20260528_040
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

revision = "20260528_050"
down_revision = "20260528_040"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- leads: new AI-derived fields ---
    op.add_column("leads", sa.Column("engagement_likelihood", sa.Float(), nullable=True))
    op.add_column("leads", sa.Column("response_probability", sa.Float(), nullable=True))
    op.add_column("leads", sa.Column("campaign_fit_score", sa.Float(), nullable=True))
    op.add_column("leads", sa.Column("role_influence", sa.String(20), nullable=True))
    op.add_column("leads", sa.Column("personality_style", sa.String(50), nullable=True))
    op.add_column("leads", sa.Column("linkedin_activity_level", sa.String(20), nullable=True))
    op.add_column("leads", sa.Column("buying_stage", sa.String(50), nullable=True))
    op.add_column("leads", sa.Column("preferred_campaign_type", sa.String(50), nullable=True))
    op.add_column("leads", sa.Column("likely_pain_points", ARRAY(sa.Text()), nullable=True))
    op.add_column("leads", sa.Column("likely_kpis", ARRAY(sa.Text()), nullable=True))
    op.add_column("leads", sa.Column("outreach_angles", ARRAY(sa.Text()), nullable=True))
    op.add_column("leads", sa.Column("buying_signals", ARRAY(sa.Text()), nullable=True))
    op.add_column("leads", sa.Column("risk_flags", ARRAY(sa.Text()), nullable=True))
    op.add_column("leads", sa.Column("campaign_recommendations", JSONB(), nullable=True))
    op.add_column("leads", sa.Column("signals", JSONB(), nullable=True))

    # --- companies: growth & operational profile ---
    op.add_column("companies", sa.Column("business_model", sa.String(100), nullable=True))
    op.add_column("companies", sa.Column("growth_stage", sa.String(30), nullable=True))
    op.add_column("companies", sa.Column("multi_location", sa.Boolean(), nullable=True))
    op.add_column("companies", sa.Column("operational_complexity", sa.String(20), nullable=True))
    op.add_column("companies", sa.Column("supply_chain_complexity", sa.String(20), nullable=True))
    op.add_column("companies", sa.Column("expansion_signals", ARRAY(sa.Text()), nullable=True))
    op.add_column("companies", sa.Column("recent_business_events", ARRAY(sa.Text()), nullable=True))
    op.add_column("companies", sa.Column("likely_business_goals", ARRAY(sa.Text()), nullable=True))
    op.add_column("companies", sa.Column("procurement_maturity", sa.String(20), nullable=True))
    op.add_column("companies", sa.Column("vendor_dependency_likelihood", sa.String(20), nullable=True))
    op.add_column("companies", sa.Column("tools_detected", ARRAY(sa.Text()), nullable=True))
    op.add_column("companies", sa.Column("brand_maturity_score", sa.Float(), nullable=True))
    op.add_column("companies", sa.Column("technology_maturity", sa.String(20), nullable=True))
    op.add_column("companies", sa.Column("digital_maturity", sa.String(20), nullable=True))
    op.add_column("companies", sa.Column("estimated_monthly_traffic", sa.String(50), nullable=True))
    op.add_column("companies", sa.Column("competitive_intelligence", JSONB(), nullable=True))
    op.add_column("companies", sa.Column("marketing_signals", JSONB(), nullable=True))


def downgrade() -> None:
    for col in [
        "engagement_likelihood", "response_probability", "campaign_fit_score",
        "role_influence", "personality_style", "linkedin_activity_level",
        "buying_stage", "preferred_campaign_type", "likely_pain_points",
        "likely_kpis", "outreach_angles", "buying_signals", "risk_flags",
        "campaign_recommendations", "signals",
    ]:
        op.drop_column("leads", col)

    for col in [
        "business_model", "growth_stage", "multi_location",
        "operational_complexity", "supply_chain_complexity",
        "expansion_signals", "recent_business_events", "likely_business_goals",
        "procurement_maturity", "vendor_dependency_likelihood",
        "tools_detected", "brand_maturity_score", "technology_maturity",
        "digital_maturity", "estimated_monthly_traffic",
        "competitive_intelligence", "marketing_signals",
    ]:
        op.drop_column("companies", col)
