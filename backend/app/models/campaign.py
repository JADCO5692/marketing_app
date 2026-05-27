import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from app.database import Base


class Campaign(Base):
    """Schema ready from day 1; sending engine activates in Phase 9."""
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    segment_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("segments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="draft")  # draft/scheduled/sending/sent/paused
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    open_count: Mapped[int] = mapped_column(Integer, default=0)
    click_count: Mapped[int] = mapped_column(Integer, default=0)
    bounce_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
