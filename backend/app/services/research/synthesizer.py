"""
Claude synthesis step — merges all raw research sources into structured KPI JSON.
This is the final step in the research pipeline, after scrape + search + email verify.
"""
from app.services.ai_client import chat_json

SYNTHESIS_SYSTEM = """
You are a B2B sales intelligence analyst. You receive raw research data about a company
and a contact, and you synthesize it into structured enrichment data.

Return ONLY valid JSON with this exact structure — no markdown, no extra text:
{
  "company": {
    "industry": "string",
    "sub_industry": "string",
    "business_type": "B2B | B2C | B2B2C",
    "company_size": "SME | Mid-market | Enterprise",
    "headcount_range": "string e.g. 50-200",
    "revenue_range": "string e.g. $1M-$10M",
    "funding_stage": "Bootstrap | Seed | Series A | Series B | Series C+ | Public",
    "region": "string",
    "country": "string",
    "city": "string",
    "hiring_velocity": "High | Medium | Low | None",
    "tech_stack": ["tool1", "tool2"],
    "pain_points": ["pain1", "pain2"],
    "website_quality_score": 0-10,
    "social_presence_score": 0-10,
    "traffic_estimate": "string e.g. <10K/mo"
  },
  "lead": {
    "seniority_level": "C-Suite | VP | Director | Manager | IC",
    "department": "string",
    "is_decision_maker": true | false,
    "budget_authority": true | false,
    "icp_score": 0-100,
    "intent_score": 0-100,
    "engagement_readiness": 0-100,
    "campaign_type_match": "educational | demo | case_study | offer | nurture",
    "personalization_tags": ["tag1", "tag2"],
    "competitive_intel": {"current_tools": [], "pain_context": ""},
    "pain_point_clusters": ["pain1", "pain2"]
  }
}

Scoring guidelines:
- icp_score: 0=no fit, 100=perfect fit for a B2B SaaS product
- intent_score: based on hiring signals, recent funding, news activity, tool switches
- engagement_readiness: based on seniority, email availability, company activity
"""


async def synthesize(
    lead_raw: dict,
    company_raw: dict,
    website_data: dict,
    search_results: list[dict],
    email_verification: dict,
) -> dict | None:
    """
    Synthesize all research into structured KPI fields.
    Returns None on failure so the worker can log and continue.
    """
    prompt = f"""
Contact raw data:
{lead_raw}

Company raw data:
{company_raw}

Website scrape:
{website_data}

Search results:
{search_results[:5]}

Email verification:
{email_verification}

Synthesize all of this into the structured JSON format.
"""
    try:
        return await chat_json(SYNTHESIS_SYSTEM, prompt, max_tokens=1500)
    except Exception:
        return None
