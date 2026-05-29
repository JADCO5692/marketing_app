"""
Settings service — DB-first with env-var fallback.

`get_setting(key)` is synchronous and safe to call anywhere.
Call `load_overrides(db)` at app startup and after any write to populate
the in-memory cache so services don't need a DB session at call-time.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings as env_settings

# In-memory override cache populated at startup and on each write
_overrides: dict[str, str] = {}

SENSITIVE_KEYS = {
    "CLAUDE_API_KEY", "OPENAI_API_KEY", "SERPER_API_KEY",
    "HUNTER_API_KEY", "TAVILY_API_KEY", "APOLLO_API_KEY", "GEMINI_API_KEY",
}

_DEFAULT_RESEARCH_PROMPT = """\
You are an AI-powered B2B revenue intelligence and lead enrichment engine.

Your job is to analyze raw research data about a company and contact, then extract every possible sales, marketing, intent, operational, and personalization signal that could help outbound campaigns, ABM campaigns, SDR outreach, retargeting, lead scoring, and segmentation.

Your objective is NOT just to summarize the company.
Your objective is to uncover actionable GTM intelligence.

You should infer missing information when strong signals exist, but avoid hallucinating unsupported facts.

Analyze:
* Company website
* LinkedIn/company descriptions
* Job postings
* Tech stack indicators
* News mentions
* Social activity
* Reviews/testimonials
* Funding signals
* Hiring trends
* Product/service offerings
* Operations/logistics indicators
* Ecommerce indicators
* Expansion indicators
* Procurement or supply-chain indicators
* Public partnerships
* Market positioning
* Competitive signals
* Any operational complexity or scale indicators

Focus heavily on identifying:
* Buying intent
* Operational maturity
* Growth signals
* Expansion activity
* Pain points
* Decision-maker relevance
* Campaign opportunities
* Outreach personalization angles
* Industry-specific triggers
* Budget likelihood
* Vendor-switching indicators
* Technology adoption maturity
* Procurement complexity
* Multi-location operations
* Supply-chain scale
* Seasonal or event-driven opportunities

Return ONLY valid JSON.
Do not return markdown.
Do not explain anything.
Do not include comments.

Return this exact structure:
{
  "company": {
    "name": "",
    "industry": "",
    "sub_industry": "",
    "business_model": "",
    "business_type": "B2B | B2C | B2B2C | D2C | Marketplace",
    "company_size": "Startup | SME | Mid-market | Enterprise",
    "headcount_range": "",
    "revenue_range": "",
    "funding_stage": "Bootstrap | Seed | Series A | Series B | Series C+ | Public | Unknown",
    "growth_stage": "Early | Growth | Scaling | Mature | Declining",
    "region": "",
    "country": "",
    "city": "",
    "multi_location": true,
    "operational_complexity": "Low | Medium | High",
    "supply_chain_complexity": "Low | Medium | High",
    "hiring_velocity": "High | Medium | Low | None",
    "expansion_signals": [],
    "recent_business_events": [],
    "technology_maturity": "Low | Medium | High",
    "digital_maturity": "Low | Medium | High",
    "estimated_monthly_traffic": "",
    "social_presence_score": 0,
    "website_quality_score": 0,
    "brand_maturity_score": 0,
    "tech_stack": [],
    "tools_detected": [],
    "pain_points": [],
    "likely_business_goals": [],
    "procurement_maturity": "Low | Medium | High",
    "vendor_dependency_likelihood": "Low | Medium | High",
    "competitive_intelligence": {
      "competitors_mentioned": [],
      "current_vendors": [],
      "possible_vendor_switch_signals": [],
      "pricing_pressure_signals": []
    },
    "marketing_signals": {
      "active_ads_detected": true,
      "seo_maturity": "Low | Medium | High",
      "content_marketing_activity": "Low | Medium | High",
      "social_activity_level": "Low | Medium | High"
    }
  },
  "lead": {
    "full_name": "",
    "job_title": "",
    "department": "",
    "seniority_level": "C-Suite | VP | Director | Manager | IC",
    "role_influence": "Low | Medium | High",
    "is_decision_maker": true,
    "budget_authority": true,
    "likely_kpis": [],
    "likely_pain_points": [],
    "personality_style": "Analytical | Operational | Financial | Strategic | Technical | Unknown",
    "linkedin_activity_level": "High | Medium | Low | Unknown",
    "engagement_likelihood": 0,
    "response_probability": 0,
    "preferred_campaign_type": "educational | demo | case_study | offer | nurture | comparison",
    "personalization_tags": [],
    "outreach_angles": [],
    "buying_stage": "Unaware | Problem Aware | Solution Aware | Vendor Evaluating | Ready to Buy",
    "buying_signals": [],
    "risk_flags": [],
    "campaign_fit_score": 0,
    "icp_score": 0,
    "intent_score": 0,
    "engagement_readiness": 0
  },
  "campaign_recommendations": {
    "recommended_channels": [],
    "recommended_sequence_type": "",
    "recommended_offer": "",
    "recommended_cta": "",
    "best_hooks": [],
    "best_value_propositions": [],
    "recommended_case_study_angles": [],
    "urgency_level": "Low | Medium | High",
    "sales_priority": "Low | Medium | High | Immediate"
  },
  "signals": {
    "growth_signals": [],
    "buying_signals": [],
    "operational_signals": [],
    "technology_signals": [],
    "logistics_signals": [],
    "marketing_signals": [],
    "risk_signals": [],
    "expansion_signals": []
  }
}

Scoring Guidelines:
* icp_score: 0=no relevance to target market, 50=partial fit, 100=perfect target customer
* intent_score: based on operational expansion, hiring, procurement activity, funding, partnerships, technology changes, logistics growth, warehouse activity, or buying-related signals
* engagement_readiness: based on contact seniority, company activity, digital maturity, and available outreach channels
* campaign_fit_score: measures how suitable the lead is for immediate outbound or marketing campaigns

Important Rules:
* Infer intelligently from weak signals.
* Use "Unknown" when confidence is low.
* Never invent exact numbers unless evidence strongly suggests them.
* Prefer probabilistic reasoning over empty fields.
* Extract every useful signal possible from limited data.
* Think like an SDR + growth marketer + revenue operations analyst combined.\
"""

SETTINGS_META = [
    {
        "group": "Research",
        "items": [
            {"key": "RESEARCH_PROMPT_TEMPLATE", "label": "Research Prompt Template", "type": "textarea",
             "description": "System prompt used by the AI synthesis step. Defines the persona, analysis focus, and exact JSON output structure the AI must return. Edit to tune scoring, add industry-specific context, or change what signals are extracted. Changes take effect on the next research job — no restart needed.",
             "default": _DEFAULT_RESEARCH_PROMPT},
        ],
    },
    {
        "group": "AI Models",
        "items": [
            {"key": "CLAUDE_API_KEY",  "label": "Claude API Key",  "type": "secret",
             "description": "Anthropic API key — used for research synthesis and lead classification. Get one at console.anthropic.com."},
            {"key": "CLAUDE_MODEL",    "label": "Claude Model",    "type": "text",
             "description": "Model ID to use (e.g. claude-sonnet-4-6). Defaults to the value in .env."},
            {"key": "OPENAI_API_KEY",  "label": "OpenAI API Key",  "type": "secret",
             "description": "Used for text-embedding-3-small to generate lead embeddings for semantic deduplication."},
            {"key": "GEMINI_API_KEY",  "label": "Gemini API Key",  "type": "secret",
             "description": "Google Gemini API key — optional alternative AI provider. Get one at aistudio.google.com."},
        ],
    },
    {
        "group": "Research APIs",
        "items": [
            {"key": "SERPER_API_KEY",  "label": "Serper API Key",  "type": "secret",
             "description": "Google Search via serper.dev — free 2,500 queries/mo. Used for company research."},
            {"key": "HUNTER_API_KEY",  "label": "Hunter.io API Key","type": "secret",
             "description": "Email verification and discovery — free 25 verifications/mo at hunter.io."},
            {"key": "TAVILY_API_KEY",  "label": "Tavily API Key",   "type": "secret",
             "description": "AI-optimised search (optional alternative to Serper) — free tier available at tavily.com."},
            {"key": "APOLLO_API_KEY",  "label": "Apollo API Key",   "type": "secret",
             "description": "Full contact + company enrichment (optional) — free tier at apollo.io."},
        ],
    },
    {
        "group": "Deduplication",
        "items": [
            {"key": "DEDUP_AUTO_MERGE_THRESHOLD",  "label": "Auto-merge Threshold",  "type": "number",
             "description": "Cosine similarity (0–1) above which two leads are automatically merged. Default: 0.97."},
            {"key": "DEDUP_REVIEW_THRESHOLD",      "label": "Review Threshold",       "type": "number",
             "description": "Cosine similarity above which a pair is flagged for manual review. Default: 0.92."},
        ],
    },
    {
        "group": "Feature Flags",
        "items": [
            {"key": "RESEARCH_ENABLED",               "label": "Research Enabled",        "type": "bool",
             "description": "Globally enable or disable the AI research pipeline."},
            {"key": "MAX_CONCURRENT_RESEARCH_WORKERS","label": "Max Research Workers",    "type": "number",
             "description": "Maximum concurrent research jobs in the ARQ worker. Default: 4."},
        ],
    },
]


def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """Return DB override if set, else env var, else default."""
    if key in _overrides and _overrides[key]:
        return _overrides[key]
    val = getattr(env_settings, key, None)
    if val is not None:
        return str(val)
    return default


def _mask(value: str) -> str:
    if len(value) <= 4:
        return "●" * len(value)
    return "●" * (len(value) - 4) + value[-4:]


async def load_overrides(db: AsyncSession) -> None:
    from app.models.app_setting import AppSetting
    result = await db.execute(select(AppSetting))
    _overrides.clear()
    for row in result.scalars().all():
        if row.value:
            _overrides[row.key] = row.value


async def list_settings(db: AsyncSession) -> list[dict]:
    from app.models.app_setting import AppSetting
    result = await db.execute(select(AppSetting))
    db_rows = {r.key: r for r in result.scalars().all()}

    out = []
    for group in SETTINGS_META:
        for item in group["items"]:
            key = item["key"]
            db_row = db_rows.get(key)
            env_val = str(getattr(env_settings, key, "") or "")

            # Determine display source and value
            if db_row and db_row.value:
                source = "db"
                display = _mask(db_row.value) if item["type"] == "secret" else db_row.value
            elif env_val:
                source = "env"
                display = _mask(env_val) if item["type"] == "secret" else env_val
            else:
                source = "unset"
                display = ""

            out.append({
                **item,
                "group": group["group"],
                "value": display,
                "source": source,
                "updated_at": db_row.updated_at.isoformat() if db_row else None,
            })
    return out


def _sanitize(value: str) -> str:
    """Strip whitespace and invisible Unicode characters (zero-width spaces, BOM, etc.)."""
    return "".join(ch for ch in value if ch.isprintable()).strip()


async def upsert_setting(db: AsyncSession, key: str, value: str) -> None:
    from app.models.app_setting import AppSetting
    from datetime import datetime, timezone
    clean = _sanitize(value)
    result = await db.execute(select(AppSetting).where(AppSetting.key == key))
    row = result.scalar_one_or_none()
    if row:
        row.value = clean
        row.updated_at = datetime.now(timezone.utc)
    else:
        db.add(AppSetting(key=key, value=clean))
    await db.commit()
    _overrides[key] = clean


async def delete_setting(db: AsyncSession, key: str) -> None:
    from app.models.app_setting import AppSetting
    result = await db.execute(select(AppSetting).where(AppSetting.key == key))
    row = result.scalar_one_or_none()
    if row:
        await db.delete(row)
        await db.commit()
    _overrides.pop(key, None)
