from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class SegmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    filter_rules: dict = {}


class SegmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    filter_rules: Optional[dict] = None


class SegmentResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    filter_rules: dict
    lead_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SegmentPreviewResponse(BaseModel):
    lead_count: int
    sample_leads: list[dict]
