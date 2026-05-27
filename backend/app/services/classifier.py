"""
AI classification pipeline.
Takes a lead + company research data and returns structured KPI fields.
Phase 5 implementation — stubs return None until Phase 5 is built.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.lead import Lead

CLASSIFICATION_SYSTEM = """
You are a B2B sales intelligence analyst. Given a lead and their company information,
classify them across multiple dimensions and return a structured JSON object.

Return ONLY valid JSON, no markdown, no explanation.

Required JSON structure:
{
  "industry": "string (e.g. SaaS, FinTech, Healthcare, Manufacturing, Retail)",
  "sub_industry": "string (e.g. HR Tech, Payments, Telemedicine)",
  "business_type": "B2B | B2C | B2B2C",
  "company_size": "SME | Mid-market | Enterprise",
  "icp_score": 0-100,
  "intent_score": 0-100,
  "engagement_readiness": 0-100,
  "campaign_type_match": "educational | demo | case_study | offer | nurture",
  "personalization_tags": ["tag1", "tag2"],
  "pain_point_clusters": ["pain1", "pain2"],
  "is_decision_maker": true | false | null,
  "budget_authority": true | false | null,
  "seniority_level": "C-Suite | VP | Director | Manager | IC | null"
}
"""


async def classify_lead(lead_data: dict, company_data: dict, research_data: dict) -> dict | None:
    """
    Classify a lead using Claude. Returns a dict of KPI fields or None on failure.
    Phase 5 wires this to real logic. For now returns None so the worker gracefully skips.
    """
    if not lead_data and not company_data:
        return None

    from app.services.ai_client import chat_json

    prompt = f"""
Lead information:
{lead_data}

Company information:
{company_data}

Research findings:
{research_data}

Classify this lead and return the JSON object as specified.
"""
    try:
        result = await chat_json(CLASSIFICATION_SYSTEM, prompt, max_tokens=1000)
        return result
    except Exception:
        return None
