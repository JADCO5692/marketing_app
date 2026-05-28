from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid


class LeadCreate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    department: Optional[str] = None
    seniority_level: Optional[str] = None


class LeadBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    seniority_level: Optional[str] = None


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    seniority_level: Optional[str] = None
    is_decision_maker: Optional[bool] = None
    budget_authority: Optional[bool] = None
    icp_score: Optional[float] = None
    intent_score: Optional[float] = None
    engagement_readiness: Optional[float] = None
    campaign_type_match: Optional[str] = None
    personalization_tags: Optional[list[str]] = None
    pain_point_clusters: Optional[list[str]] = None
    status: Optional[str] = None


class LeadResponse(BaseModel):
    id: uuid.UUID
    company_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    email: Optional[str] = None
    email_verified: bool
    email_type: Optional[str] = None
    email_deliverability: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    seniority_level: Optional[str] = None
    is_decision_maker: Optional[bool] = None
    budget_authority: Optional[bool] = None
    icp_score: Optional[float] = None
    intent_score: Optional[float] = None
    engagement_readiness: Optional[float] = None
    campaign_type_match: Optional[str] = None
    personalization_tags: Optional[list[str]] = None
    competitive_intel: Optional[dict] = None
    pain_point_clusters: Optional[list[str]] = None
    status: str
    arq_job_id: Optional[str] = None
    duplicate_of: Optional[uuid.UUID] = None
    source_file: Optional[str] = None
    source_row: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadListParams(BaseModel):
    status: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    company_size: Optional[str] = None
    funding_stage: Optional[str] = None
    icp_score_min: Optional[float] = None
    icp_score_max: Optional[float] = None
    is_decision_maker: Optional[bool] = None
    email_verified: Optional[bool] = None
    search: Optional[str] = None
    limit: int = 50
    offset: int = 0


class DuplicatePair(BaseModel):
    lead_a: LeadResponse
    lead_b: LeadResponse
    similarity: float
    auto_suggested: bool
