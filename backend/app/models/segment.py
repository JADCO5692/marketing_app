import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PgUUID, JSONB
from app.database import Base


class Segment(Base):
    __tablename__ = "segments"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # e.g. {"icp_score": {">": 70}, "region": "Asia", "company_size": ["SME", "Mid-market"]}
    filter_rules: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    lead_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
