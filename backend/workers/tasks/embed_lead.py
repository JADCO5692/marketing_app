"""
Generate and store pgvector embedding for a lead.
Runs after research so name+company+title are all populated.
Then triggers semantic duplicate detection.
"""
import uuid
from app.database import AsyncSessionLocal
from app.models.lead import Lead
from app.services.embeddings import embed_lead as _embed
from app.services.deduplicator import process_semantic_dedup


async def embed_lead(ctx: dict, lead_id: str) -> dict:
    async with AsyncSessionLocal() as db:
        lead = await db.get(Lead, uuid.UUID(lead_id))
        if not lead:
            return {"error": "Lead not found"}

        embedding = await _embed({
            "name": lead.name,
            "job_title": lead.job_title,
            "company_name": (lead.raw_csv_data or {}).get("company_name", ""),
            "department": lead.department,
        })

        if embedding:
            lead.embedding = embedding
            await db.commit()
            flagged = await process_semantic_dedup(db, lead)
            await db.commit()
            return {"lead_id": lead_id, "embedded": True, "duplicates_flagged": flagged}

        return {"lead_id": lead_id, "embedded": False}
