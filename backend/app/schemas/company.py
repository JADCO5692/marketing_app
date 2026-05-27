from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    business_type: Optional[str] = None
    company_size: Optional[str] = None
    headcount_range: Optional[str] = None
    revenue_range: Optional[str] = None
    funding_stage: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    tech_stack: Optional[list[str]] = None
    pain_points: Optional[list[str]] = None


class CompanyResponse(BaseModel):
    id: uuid.UUID
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    business_type: Optional[str] = None
    company_size: Optional[str] = None
    headcount_range: Optional[str] = None
    revenue_range: Optional[str] = None
    funding_stage: Optional[str] = None
    years_operating: Optional[int] = None
    hiring_velocity: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    tech_stack: Optional[list[str]] = None
    pain_points: Optional[list[str]] = None
    website_quality_score: Optional[float] = None
    social_presence_score: Optional[float] = None
    traffic_estimate: Optional[str] = None
    research_status: str
    last_researched_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
