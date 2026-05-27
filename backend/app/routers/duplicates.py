from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from app.database import get_db
from app.models.lead import Lead
from app.schemas.lead import LeadResponse, DuplicatePair
from app.schemas.common import PaginatedResponse
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=PaginatedResponse[DuplicatePair])
async def list_duplicates(
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return leads flagged as duplicates, paired with their originals."""
    q = select(Lead).where(Lead.status == "duplicate", Lead.duplicate_of.isnot(None))
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    result = await db.execute(q.order_by(Lead.created_at.desc()).limit(limit).offset(offset))
    dup_leads = result.scalars().all()

    pairs: list[DuplicatePair] = []
    for dup in dup_leads:
        original = await db.get(Lead, dup.duplicate_of)
        if original:
            pairs.append(DuplicatePair(
                lead_a=LeadResponse.model_validate(original),
                lead_b=LeadResponse.model_validate(dup),
                similarity=1.0,
                auto_suggested=True,
            ))

    return PaginatedResponse(items=pairs, total=total, limit=limit, offset=offset)


@router.post("/{lead_id}/merge")
async def merge_duplicate(
    lead_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Confirm merge: keep duplicate_of (lead A), archive this lead (lead B)."""
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if not lead.duplicate_of:
        raise HTTPException(status_code=400, detail="Lead has no duplicate_of reference")

    original = await db.get(Lead, lead.duplicate_of)
    if not original:
        raise HTTPException(status_code=404, detail="Original lead not found")

    # Merge: copy non-null fields from duplicate onto original where original is null
    for field in ["phone", "linkedin_url", "job_title", "department", "seniority_level",
                  "is_decision_maker", "budget_authority"]:
        if getattr(original, field) is None and getattr(lead, field) is not None:
            setattr(original, field, getattr(lead, field))

    # Union tags
    for arr_field in ["personalization_tags", "pain_point_clusters"]:
        orig_list = getattr(original, arr_field) or []
        dup_list = getattr(lead, arr_field) or []
        merged = list(dict.fromkeys(orig_list + dup_list))
        setattr(original, arr_field, merged if merged else None)

    # Take better scores
    for score_field in ["icp_score", "intent_score", "engagement_readiness"]:
        orig_val = getattr(original, score_field)
        dup_val = getattr(lead, score_field)
        if dup_val is not None and (orig_val is None or dup_val > orig_val):
            setattr(original, score_field, dup_val)

    lead.status = "merged"
    original.status = "enriched" if original.icp_score is not None else original.status

    await db.commit()
    return {"message": "Merged successfully", "kept_id": str(original.id)}


@router.post("/{lead_id}/dismiss")
async def dismiss_duplicate(
    lead_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark lead as NOT a duplicate — restore status to raw."""
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.status = "raw"
    lead.duplicate_of = None
    await db.commit()
    return {"message": "Dismissed — lead restored to raw status"}
