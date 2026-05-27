"""
Standalone AI classification task.
Can be called independently of research (e.g. re-classify after manual data entry).
"""
import uuid
from app.database import AsyncSessionLocal
from app.models.lead import Lead
from app.models.company import Company
from app.services.classifier import classify_lead as _classify


async def classify_lead(ctx: dict, lead_id: str) -> dict:
    async with AsyncSessionLocal() as db:
        lead = await db.get(Lead, uuid.UUID(lead_id))
        if not lead:
            return {"error": "Lead not found"}

        company = await db.get(Company, lead.company_id) if lead.company_id else None

        result = await _classify(
            lead_data={"name": lead.name, "email": lead.email, "job_title": lead.job_title,
                       "department": lead.department, **(lead.raw_csv_data or {})},
            company_data={"name": company.name if company else "", "domain": company.domain if company else "",
                          "industry": company.industry if company else ""},
            research_data={},
        )

        if result:
            for field in ["icp_score", "intent_score", "engagement_readiness", "campaign_type_match",
                          "personalization_tags", "pain_point_clusters", "is_decision_maker",
                          "budget_authority", "seniority_level"]:
                val = result.get(field)
                if val is not None:
                    setattr(lead, field, val)
            await db.commit()
            return {"lead_id": lead_id, "classified": True}

        return {"lead_id": lead_id, "classified": False}
