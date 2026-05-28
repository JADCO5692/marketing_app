import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
import uuid

from app.database import get_db
from app.models.lead import Lead
from app.schemas.lead import LeadResponse, LeadUpdate, LeadCreate
from app.schemas.common import PaginatedResponse, TaskQueued
from app.services.auth import get_current_user
from app.models.user import User
from app.queue import get_queue

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


@router.post("", response_model=LeadResponse, status_code=201)
async def create_lead(
    body: LeadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.company import Company
    from sqlalchemy import select as sa_select
    company_id = None
    if body.company_name:
        res = await db.execute(
            sa_select(Company).where(Company.name == body.company_name)
        )
        company = res.scalar_one_or_none()
        if not company:
            company = Company(name=body.company_name)
            db.add(company)
            await db.flush()
        company_id = company.id

    lead = Lead(
        name=body.name,
        email=body.email,
        phone=body.phone,
        linkedin_url=body.linkedin_url,
        job_title=body.job_title,
        department=body.department,
        seniority_level=body.seniority_level,
        company_id=company_id,
        status="raw",
        raw_csv_data={"company_name": body.company_name} if body.company_name else {},
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.delete("", status_code=200)
async def delete_all_leads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import delete as sa_delete
    result = await db.execute(sa_delete(Lead))
    await db.commit()
    return {"deleted": result.rowcount}


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
    lead.status = "researching"
    queue = await get_queue()
    job = await queue.enqueue_job("research_lead", str(lead_id))
    lead.arq_job_id = job.job_id if job else None
    await db.commit()
    return TaskQueued(task_id=job.job_id if job else str(lead_id), message="Research task queued")


@router.post("/{lead_id}/cancel-research", response_model=TaskQueued)
async def cancel_research(
    lead_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if lead.status != "researching":
        raise HTTPException(status_code=400, detail="Lead is not in research queue")

    # Best-effort ARQ job abort
    if lead.arq_job_id:
        try:
            from arq.jobs import Job
            queue = await get_queue()
            job = Job(job_id=lead.arq_job_id, redis=queue)
            await job.abort()
        except Exception:
            pass

    lead.status = "raw"
    lead.arq_job_id = None
    await db.commit()
    return TaskQueued(task_id=str(lead_id), message="Research cancelled")
