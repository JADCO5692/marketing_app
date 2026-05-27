from pydantic import BaseModel
from typing import Optional


class OverviewStats(BaseModel):
    total_leads: int
    enriched_leads: int
    enriched_pct: float
    avg_icp_score: Optional[float]
    decision_maker_pct: float
    email_verified_pct: float
    duplicate_count: int
    research_pending: int


class GroupedStat(BaseModel):
    label: str
    count: int
    avg_icp_score: Optional[float] = None
    avg_intent_score: Optional[float] = None


class HistogramBucket(BaseModel):
    bucket_start: float
    bucket_end: float
    count: int


class ResearchCostStat(BaseModel):
    source: str
    call_count: int
    total_cost_usd: float
    success_rate: float
