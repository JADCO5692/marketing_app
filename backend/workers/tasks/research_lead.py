"""
Full research pipeline for a single lead.
Steps run concurrently: website scrape + Google search + email verify.
Only steps with configured API keys are executed.
Active AI provider (Claude / Gemini / OpenAI) is auto-selected from Settings.
"""
import asyncio
import time
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.lead import Lead
from app.models.company import Company
from app.models.research_log import ResearchLog
from app.models.app_setting import AppSetting
from app.services.settings_service import get_setting


async def _timed(coro) -> tuple:
    """Run a coroutine and return (result, duration_ms)."""
    t0 = time.monotonic()
    result = await coro
    return result, round((time.monotonic() - t0) * 1000)


async def research_lead(ctx: dict, lead_id: str) -> dict:
    """
    ARQ task: run the full research pipeline for a lead.
    Idempotent: if called twice, the second run overwrites with fresher data.
    """
    from app.services.research.scraper import scrape_website
    from app.services.research.search import research_company
    from app.services.research.email_verify import verify_email
    from app.services.research.synthesizer import synthesize

    async with AsyncSessionLocal() as db:
        # Check global pause flag (queried fresh from DB, not from cache)
        pause_row = (await db.execute(
            select(AppSetting).where(AppSetting.key == "RESEARCH_PAUSED")
        )).scalar_one_or_none()
        if pause_row and pause_row.value == "true":
            return {"lead_id": lead_id, "status": "paused"}

        lead = await db.get(Lead, uuid.UUID(lead_id))
        if not lead:
            return {"error": "Lead not found", "lead_id": lead_id}

        lead.status = "researching"
        await db.commit()

        company = (
            await db.get(Company, lead.company_id)
            if lead.company_id else None
        )
        domain = company.domain if company else None
        company_name = (
            company.name if company
            else (lead.raw_csv_data or {}).get("company_name", "")
        )

        has_serper = bool(get_setting("SERPER_API_KEY"))
        has_hunter = bool(get_setting("HUNTER_API_KEY"))

        website_task = (
            _timed(scrape_website(domain))
            if domain
            else _timed(asyncio.sleep(0, result={}))
        )
        search_task = (
            _timed(research_company(company_name, domain))
            if (has_serper and company_name)
            else _timed(asyncio.sleep(0, result={}))
        )
        email_task = (
            _timed(verify_email(lead.email))
            if (has_hunter and lead.email)
            else _timed(asyncio.sleep(0, result={}))
        )

        (website_data, w_ms), (search_data, s_ms), (email_data, e_ms) = (
            await asyncio.gather(website_task, search_task, email_task)
        )

        for source, data, query, ran, dur in [
            ("playwright", website_data, domain, bool(domain), w_ms),
            (
                "serper", search_data, company_name,
                has_serper and bool(company_name), s_ms,
            ),
            (
                "hunter", email_data, lead.email,
                has_hunter and bool(lead.email), e_ms,
            ),
        ]:
            if not ran:
                continue
            log = ResearchLog(
                lead_id=lead.id,
                source=source,
                query=query,
                raw_response=data if isinstance(data, dict) else {},
                success="error" not in (data or {}),
                error=(data or {}).get("error"),
                duration_ms=dur,
            )
            db.add(log)

        ai_provider = (
            "claude" if get_setting("CLAUDE_API_KEY")
            else "gemini" if get_setting("GEMINI_API_KEY")
            else "openai" if get_setting("OPENAI_API_KEY")
            else None
        )

        result = None
        if ai_provider:
            result, synth_ms = await _timed(synthesize(
                lead_raw={
                    "name": lead.name,
                    "email": lead.email,
                    "job_title": lead.job_title,
                    "department": lead.department,
                    **(lead.raw_csv_data or {}),
                },
                company_raw={"name": company_name, "domain": domain},
                website_data=website_data,
                search_results=search_data.get("results", []),
                email_verification=email_data,
            ))

            synth_log = ResearchLog(
                lead_id=lead.id,
                source=ai_provider,
                query="synthesis",
                raw_response=result or {},
                success=result is not None,
                error=None if result else "Synthesis returned no data",
                duration_ms=synth_ms,
            )
            db.add(synth_log)
        else:
            synth_log = ResearchLog(
                lead_id=lead.id,
                source="ai",
                query="synthesis",
                raw_response={},
                success=False,
                error=(
                    "No AI provider configured "
                    "(set CLAUDE_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY "
                    "in Settings)"
                ),
            )
            db.add(synth_log)

        # Check if the lead was cancelled while we were running
        await db.refresh(lead)
        if lead.status != "researching":
            return {"lead_id": lead_id, "status": "cancelled"}

        if result:
            if email_data.get("status"):
                lead.email_deliverability = email_data["status"]
                lead.email_verified = (
                    email_data["status"] == "deliverable"
                )
                lead.email_type = email_data.get("email_type")

            lead_kpis = result.get("lead", {})
            for field in [
                "seniority_level", "department", "is_decision_maker",
                "budget_authority", "icp_score", "intent_score",
                "engagement_readiness", "personalization_tags",
                # new enrichment fields
                "role_influence", "personality_style",
                "linkedin_activity_level", "buying_stage",
                "preferred_campaign_type", "likely_kpis",
                "likely_pain_points", "outreach_angles",
                "buying_signals", "risk_flags",
                "engagement_likelihood", "response_probability",
                "campaign_fit_score",
            ]:
                val = lead_kpis.get(field)
                if val is not None:
                    setattr(lead, field, val)

            # keep legacy fields in sync for backward compat
            if lead_kpis.get("preferred_campaign_type"):
                lead.campaign_type_match = lead_kpis["preferred_campaign_type"]
            if lead_kpis.get("likely_pain_points"):
                lead.pain_point_clusters = lead_kpis["likely_pain_points"]

            # top-level blobs
            if result.get("campaign_recommendations"):
                lead.campaign_recommendations = result["campaign_recommendations"]
            if result.get("signals"):
                lead.signals = result["signals"]

            if company and result.get("company"):
                co = result["company"]
                for field in [
                    "industry", "sub_industry", "business_type",
                    "company_size", "headcount_range", "revenue_range",
                    "funding_stage", "region", "country", "city",
                    "hiring_velocity", "tech_stack", "pain_points",
                    "website_quality_score", "social_presence_score",
                    # new company fields
                    "business_model", "growth_stage", "multi_location",
                    "operational_complexity", "supply_chain_complexity",
                    "expansion_signals", "recent_business_events",
                    "likely_business_goals", "procurement_maturity",
                    "vendor_dependency_likelihood", "tools_detected",
                    "brand_maturity_score", "technology_maturity",
                    "digital_maturity", "estimated_monthly_traffic",
                    "competitive_intelligence", "marketing_signals",
                ]:
                    val = co.get(field)
                    if val is not None:
                        setattr(company, field, val)
                company.research_status = "done"
                company.last_researched_at = datetime.now(timezone.utc)

            lead.status = "enriched"
        else:
            lead.status = "research_failed"

        lead.arq_job_id = None
        await db.commit()

    return {"lead_id": lead_id, "status": lead.status}
