from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from app.database import get_db
from app.models.company import Company
from app.models.lead import Lead
from app.schemas.company import CompanyResponse, CompanyUpdate
from app.schemas.lead import LeadResponse
from app.schemas.common import PaginatedResponse, TaskQueued
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CompanyResponse])
async def list_companies(
    industry: str | None = Query(None),
    region: str | None = Query(None),
    funding_stage: str | None = Query(None),
    research_status: str | None = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Company)
    if industry:
        q = q.where(Company.industry == industry)
    if region:
        q = q.where(Company.region == region)
    if funding_stage:
        q = q.where(Company.funding_stage == funding_stage)
    if research_status:
        q = q.where(Company.research_status == research_status)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    result = await db.execute(q.order_by(Company.created_at.desc()).limit(limit).offset(offset))
    return PaginatedResponse(items=result.scalars().all(), total=total, limit=limit, offset=offset)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/{company_id}/leads", response_model=PaginatedResponse[LeadResponse])
async def get_company_leads(
    company_id: uuid.UUID,
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Lead).where(Lead.company_id == company_id)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    result = await db.execute(q.order_by(Lead.created_at.desc()).limit(limit).offset(offset))
    return PaginatedResponse(items=result.scalars().all(), total=total, limit=limit, offset=offset)


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: uuid.UUID,
    body: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    await db.commit()
    await db.refresh(company)
    return company


@router.post("/{company_id}/research", response_model=TaskQueued)
async def trigger_company_research(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    company.research_status = "pending"
    await db.commit()
    return TaskQueued(task_id=str(company_id), message="Company research task queued")
