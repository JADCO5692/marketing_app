import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
import uuid

from app.database import get_db
from app.models.lead import Lead
from app.schemas.lead import LeadResponse, LeadUpdate
from app.schemas.common import PaginatedResponse, TaskQueued
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter()


def _apply_filters(query, status, icp_score_min, icp_score_max, is_decision_maker, email_verified, search):
    if status:
        query = query.where(Lead.status == status)
    if icp_score_min is not None:
        query = query.where(Lead.icp_score >= icp_score_min)
    if icp_score_max is not None:
        query = query.where(Lead.icp_score <= icp_score_max)
    if is_decision_maker is not None:
        query = query.where(Lead.is_decision_maker == is_decision_maker)
    if email_verified is not None:
        query = query.where(Lead.email_verified == email_verified)
    if search:
        term = f"%{search}%"
        query = query.where(or_(Lead.name.ilike(term), Lead.email.ilike(term), Lead.job_title.ilike(term)))
    return query


@router.get("", response_model=PaginatedResponse[LeadResponse])
async def list_leads(
    status: str | None = Query(None),
    icp_score_min: float | None = Query(None),
    icp_score_max: float | None = Query(None),
    is_decision_maker: bool | None = Query(None),
    email_verified: bool | None = Query(None),
    search: str | None = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base = select(Lead)
    base = _apply_filters(base, status, icp_score_min, icp_score_max, is_decision_maker, email_verified, search)

    count_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_q)).scalar_one()

    result = await db.execute(base.order_by(Lead.created_at.desc()).limit(limit).offset(offset))
    leads = result.scalars().all()
    return PaginatedResponse(items=leads, total=total, limit=limit, offset=offset)


@router.get("/export")
async def export_leads(
    status: str | None = Query(None),
    icp_score_min: float | None = Query(None),
    icp_score_max: float | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Lead)
    q = _apply_filters(q, status, icp_score_min, icp_score_max, None, None, None)
    result = await db.execute(q.order_by(Lead.created_at.desc()))
    leads = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "email", "phone", "job_title", "department",
                     "seniority_level", "icp_score", "intent_score", "engagement_readiness",
                     "campaign_type_match", "status", "email_verified", "is_decision_maker", "created_at"])
    for lead in leads:
        writer.writerow([lead.id, lead.name, lead.email, lead.phone, lead.job_title,
                         lead.department, lead.seniority_level, lead.icp_score, lead.intent_score,
                         lead.engagement_readiness, lead.campaign_type_match, lead.status,
                         lead.email_verified, lead.is_decision_maker, lead.created_at])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"},
    )


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: uuid.UUID,
    body: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(lead_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.status = "invalid"
    await db.commit()


@router.post("/{lead_id}/research", response_model=TaskQueued)
async def trigger_research(
    lead_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    # Queue via ARQ — Phase 4 will wire this to the real worker
    lead.status = "researching"
    await db.commit()
    return TaskQueued(task_id=str(lead_id), message="Research task queued")
