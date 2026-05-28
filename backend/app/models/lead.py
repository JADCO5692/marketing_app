import uuid
from datetime import datetime
from sqlalchemy import String, Float, Boolean, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PgUUID, JSONB, ARRAY
from pgvector.sqlalchemy import Vector
from app.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Contact fields
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_type: Mapped[str | None] = mapped_column(String(50), nullable=True)           # personal/generic/role-based
    email_deliverability: Mapped[str | None] = mapped_column(String(50), nullable=True)  # deliverable/risky/undeliverable
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Seniority
    job_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    seniority_level: Mapped[str | None] = mapped_column(String(50), nullable=True)  # C-Suite/VP/Director/Manager/IC
    is_decision_maker: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    budget_authority: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # AI-derived KPI scores (0–100)
    icp_score: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    intent_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    engagement_readiness: Mapped[float | None] = mapped_column(Float, nullable=True)

    # AI-derived tags
    campaign_type_match: Mapped[str | None] = mapped_column(String(50), nullable=True)  # educational/demo/case_study/offer/nurture
    personalization_tags: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    competitive_intel: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    pain_point_clusters: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)

    # Raw data preservation + vector
    raw_csv_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)

    # Pipeline state
    status: Mapped[str] = mapped_column(String(30), default="raw", index=True)
    arq_job_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duplicate_of: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True
    )
    source_file: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_row: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="leads")
    research_logs: Mapped[list["ResearchLog"]] = relationship("ResearchLog", back_populates="lead", cascade="all, delete-orphan")
