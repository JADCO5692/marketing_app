from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from app.database import get_db
from app.models.lead import Lead
from app.models.research_log import ResearchLog
from app.models.company import Company
from app.schemas.analytics import OverviewStats, GroupedStat, HistogramBucket, ResearchCostStat
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/overview", response_model=OverviewStats)
async def overview(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = (await db.execute(select(func.count(Lead.id)))).scalar_one()
    enriched = (await db.execute(select(func.count(Lead.id)).where(Lead.status == "enriched"))).scalar_one()
    avg_icp = (await db.execute(select(func.avg(Lead.icp_score)).where(Lead.icp_score.isnot(None)))).scalar_one()
    dm_total = (await db.execute(select(func.count(Lead.id)).where(Lead.is_decision_maker.isnot(None)))).scalar_one()
    dm_true = (await db.execute(select(func.count(Lead.id)).where(Lead.is_decision_maker == True))).scalar_one()
    ev_true = (await db.execute(select(func.count(Lead.id)).where(Lead.email_verified == True))).scalar_one()
    dup_count = (await db.execute(select(func.count(Lead.id)).where(Lead.status == "duplicate"))).scalar_one()
    pending = (await db.execute(select(func.count(Lead.id)).where(Lead.status == "raw"))).scalar_one()

    return OverviewStats(
        total_leads=total,
        enriched_leads=enriched,
        enriched_pct=round(enriched / total * 100, 1) if total else 0.0,
        avg_icp_score=round(float(avg_icp), 1) if avg_icp else None,
        decision_maker_pct=round(dm_true / dm_total * 100, 1) if dm_total else 0.0,
        email_verified_pct=round(ev_true / total * 100, 1) if total else 0.0,
        duplicate_count=dup_count,
        research_pending=pending,
    )


@router.get("/by-industry", response_model=list[GroupedStat])
async def by_industry(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Company.industry, func.count(Lead.id), func.avg(Lead.icp_score))
        .join(Lead, Lead.company_id == Company.id, isouter=True)
        .where(Company.industry.isnot(None))
        .group_by(Company.industry)
        .order_by(func.count(Lead.id).desc())
        .limit(20)
    )
    return [GroupedStat(label=row[0], count=row[1], avg_icp_score=round(float(row[2]), 1) if row[2] else None)
            for row in result.all()]


@router.get("/by-region", response_model=list[GroupedStat])
async def by_region(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Company.region, func.count(Lead.id), func.avg(Lead.icp_score))
        .join(Lead, Lead.company_id == Company.id, isouter=True)
        .where(Company.region.isnot(None))
        .group_by(Company.region)
        .order_by(func.count(Lead.id).desc())
    )
    return [GroupedStat(label=row[0], count=row[1], avg_icp_score=round(float(row[2]), 1) if row[2] else None)
            for row in result.all()]


@router.get("/by-funding-stage", response_model=list[GroupedStat])
async def by_funding_stage(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Company.funding_stage, func.count(Lead.id))
        .join(Lead, Lead.company_id == Company.id, isouter=True)
        .where(Company.funding_stage.isnot(None))
        .group_by(Company.funding_stage)
        .order_by(func.count(Lead.id).desc())
    )
    return [GroupedStat(label=row[0], count=row[1]) for row in result.all()]


@router.get("/by-company-size", response_model=list[GroupedStat])
async def by_company_size(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Company.company_size, func.count(Lead.id))
        .join(Lead, Lead.company_id == Company.id, isouter=True)
        .where(Company.company_size.isnot(None))
        .group_by(Company.company_size)
        .order_by(func.count(Lead.id).desc())
    )
    return [GroupedStat(label=row[0], count=row[1]) for row in result.all()]


@router.get("/icp-distribution", response_model=list[HistogramBucket])
async def icp_distribution(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    buckets = [(0, 20), (20, 40), (40, 60), (60, 80), (80, 100)]
    result = []
    for start, end in buckets:
        count = (await db.execute(
            select(func.count(Lead.id)).where(Lead.icp_score >= start, Lead.icp_score < end)
        )).scalar_one()
        result.append(HistogramBucket(bucket_start=start, bucket_end=end, count=count))
    return result


@router.get("/research-cost", response_model=list[ResearchCostStat])
async def research_cost(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(
            ResearchLog.source,
            func.count(ResearchLog.id),
            func.coalesce(func.sum(ResearchLog.cost_usd), 0),
            func.avg(case((ResearchLog.success == True, 1), else_=0)),
        )
        .group_by(ResearchLog.source)
        .order_by(func.sum(ResearchLog.cost_usd).desc().nullslast())
    )
    return [
        ResearchCostStat(
            source=row[0],
            call_count=row[1],
            total_cost_usd=round(float(row[2]), 4),
            success_rate=round(float(row[3]) * 100, 1),
        )
        for row in result.all()
    ]
