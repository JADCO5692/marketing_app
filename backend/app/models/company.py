import uuid
from datetime import datetime
from sqlalchemy import String, Float, Boolean, Integer, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PgUUID, JSONB, ARRAY
from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)

    # Classification
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    sub_industry: Mapped[str | None] = mapped_column(String(150), nullable=True)
    business_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # B2B / B2C / B2B2C
    company_size: Mapped[str | None] = mapped_column(String(50), nullable=True)   # SME / Mid-market / Enterprise

    # Size signals
    headcount_range: Mapped[str | None] = mapped_column(String(50), nullable=True)
    revenue_range: Mapped[str | None] = mapped_column(String(50), nullable=True)
    funding_stage: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    years_operating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hiring_velocity: Mapped[str | None] = mapped_column(String(20), nullable=True)  # High/Medium/Low/None

    # Geography
    region: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(60), nullable=True)

    # Growth & operational profile
    business_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    growth_stage: Mapped[str | None] = mapped_column(String(30), nullable=True)
    multi_location: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    operational_complexity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    supply_chain_complexity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    expansion_signals: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    recent_business_events: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    likely_business_goals: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    procurement_maturity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    vendor_dependency_likelihood: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Digital presence
    tech_stack: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    tools_detected: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    pain_points: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    website_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    social_presence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    brand_maturity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    technology_maturity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    digital_maturity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    traffic_estimate: Mapped[str | None] = mapped_column(String(50), nullable=True)
    estimated_monthly_traffic: Mapped[str | None] = mapped_column(String(50), nullable=True)
    recent_news: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    competitive_intelligence: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    marketing_signals: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Research state
    research_status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    last_researched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    leads: Mapped[list["Lead"]] = relationship("Lead", back_populates="company")
