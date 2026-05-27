"""
Full research pipeline for a single lead.
Steps run concurrently: website scrape + Google search + email verify.
Then Claude synthesizes all results into structured KPI fields.
Phase 4 implementation.
"""
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.lead import Lead
from app.models.company import Company
from app.models.research_log import ResearchLog
from app.services.research.scraper import scrape_website
from app.services.research.search import research_company
from app.services.research.email_verify import verify_email
from app.services.research.synthesizer import synthesize


async def research_lead(ctx: dict, lead_id: str) -> dict:
    """
    ARQ task: run the full research pipeline for a lead.
    Idempotent: if called twice, the second run overwrites with fresher data.
    """
    async with AsyncSessionLocal() as db:
        lead = await db.get(Lead, uuid.UUID(lead_id))
        if not lead:
            return {"error": "Lead not found", "lead_id": lead_id}

        lead.status = "researching"
        await db.commit()

        company = await db.get(Company, lead.company_id) if lead.company_id else None
        domain = company.domain if company else None
        company_name = company.name if company else (lead.raw_csv_data or {}).get("company_name", "")

        # Steps 1–3 in parallel
        website_task = scrape_website(domain) if domain else asyncio.sleep(0, result={})
        search_task = research_company(company_name, domain) if company_name else asyncio.sleep(0, result={})
        email_task = verify_email(lead.email) if lead.email else asyncio.sleep(0, result={})

        website_data, search_data, email_data = await asyncio.gather(
            website_task, search_task, email_task
        )

        # Log each source
        for source, data, query in [
            ("playwright", website_data, domain),
            ("serper", search_data, company_name),
            ("hunter", email_data, lead.email),
        ]:
            log = ResearchLog(
                lead_id=lead.id,
                source=source,
                query=query,
                raw_response=data if isinstance(data, dict) else {},
                success="error" not in (data or {}),
                error=(data or {}).get("error"),
            )
            db.add(log)

        # Step 4: Claude synthesis
        result = await synthesize(
            lead_raw={"name": lead.name, "email": lead.email, "job_title": lead.job_title,
                      "department": lead.department, **(lead.raw_csv_data or {})},
            company_raw={"name": company_name, "domain": domain},
            website_data=website_data,
            search_results=search_data.get("results", []),
            email_verification=email_data,
        )

        synth_log = ResearchLog(
            lead_id=lead.id,
            source="claude",
            query="synthesis",
            raw_response=result or {},
            success=result is not None,
        )
        db.add(synth_log)

        if result:
            # Apply email verification fields
            if email_data.get("status"):
                lead.email_deliverability = email_data["status"]
                lead.email_verified = email_data["status"] == "deliverable"
                lead.email_type = email_data.get("email_type")

            # Apply lead KPIs from synthesis
            lead_kpis = result.get("lead", {})
            for field in ["seniority_level", "department", "is_decision_maker", "budget_authority",
                          "icp_score", "intent_score", "engagement_readiness", "campaign_type_match",
                          "personalization_tags", "competitive_intel", "pain_point_clusters"]:
                val = lead_kpis.get(field)
                if val is not None:
                    setattr(lead, field, val)

            # Apply / update company KPIs
            if company and result.get("company"):
                co = result["company"]
                for field in ["industry", "sub_industry", "business_type", "company_size",
                              "headcount_range", "revenue_range", "funding_stage", "region",
                              "country", "city", "hiring_velocity", "tech_stack", "pain_points",
                              "website_quality_score", "social_presence_score", "traffic_estimate"]:
                    val = co.get(field)
                    if val is not None:
                        setattr(company, field, val)
                company.research_status = "done"
                company.last_researched_at = datetime.now(timezone.utc)

            lead.status = "enriched"
        else:
            lead.status = "research_failed"

        await db.commit()

    return {"lead_id": lead_id, "status": lead.status}
