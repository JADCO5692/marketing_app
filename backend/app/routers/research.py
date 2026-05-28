from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from app.database import get_db
from app.models.lead import Lead
from app.models.app_setting import AppSetting
from app.models.research_log import ResearchLog
from app.schemas.common import PaginatedResponse, TaskQueued
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter()


async def _is_paused(db: AsyncSession) -> bool:
    row = (await db.execute(
        select(AppSetting).where(AppSetting.key == "RESEARCH_PAUSED")
    )).scalar_one_or_none()
    return row is not None and row.value == "true"


@router.get("/queue")
async def get_research_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Lead)
        .where(Lead.status == "researching")
        .order_by(Lead.updated_at.asc())
    )
    leads = result.scalars().all()
    items = [
        {
            "id": str(lead.id),
            "name": lead.name,
            "email": lead.email,
            "job_title": lead.job_title,
            "company_name": (lead.raw_csv_data or {}).get("company_name") if lead.raw_csv_data else None,
            "arq_job_id": lead.arq_job_id,
            "queued_at": lead.updated_at.isoformat(),
        }
        for lead in leads
    ]
    return {"items": items, "total": len(items), "paused": await _is_paused(db)}


@router.post("/cancel-all", response_model=TaskQueued)
async def cancel_all_research(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Lead).where(Lead.status == "researching"))
    leads = result.scalars().all()

    from arq.jobs import Job
    from app.queue import get_queue
    queue = await get_queue()
    for lead in leads:
        if lead.arq_job_id:
            try:
                await Job(job_id=lead.arq_job_id, redis=queue).abort()
            except Exception:
                pass
        lead.status = "raw"
        lead.arq_job_id = None

    await db.commit()
    return TaskQueued(task_id="cancel-all", message=f"{len(leads)} research jobs cancelled")


@router.post("/pause", response_model=TaskQueued)
async def pause_research(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.settings_service import upsert_setting
    await upsert_setting(db, "RESEARCH_PAUSED", "true")
    return TaskQueued(task_id="pause", message="Research paused")


@router.post("/resume", response_model=TaskQueued)
async def resume_research(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.settings_service import delete_setting
    from app.queue import get_queue
    await delete_setting(db, "RESEARCH_PAUSED")

    # Re-enqueue all leads that were held in "researching" while paused
    result = await db.execute(select(Lead).where(Lead.status == "researching"))
    leads = result.scalars().all()
    queue = await get_queue()
    for lead in leads:
        job = await queue.enqueue_job("research_lead", str(lead.id))
        lead.arq_job_id = job.job_id if job else None
    await db.commit()
    return TaskQueued(task_id="resume", message=f"Research resumed, {len(leads)} leads re-queued")


@router.get("/logs", response_model=PaginatedResponse[dict])
async def list_research_logs(
    lead_id: uuid.UUID | None = Query(None),
    source: str | None = Query(None),
    success: bool | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(ResearchLog)
    if lead_id:
        q = q.where(ResearchLog.lead_id == lead_id)
    if source:
        q = q.where(ResearchLog.source == source)
    if success is not None:
        q = q.where(ResearchLog.success == success)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    result = await db.execute(q.order_by(ResearchLog.created_at.desc()).limit(limit).offset(offset))
    logs = result.scalars().all()

    items = [
        {
            "id": str(log.id),
            "lead_id": str(log.lead_id),
            "source": log.source,
            "query": log.query,
            "success": log.success,
            "error": log.error,
            "tokens_used": log.tokens_used,
            "cost_usd": log.cost_usd,
            "duration_ms": log.duration_ms,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
    return PaginatedResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("/retry-failed", response_model=TaskQueued)
async def retry_failed(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Re-queue all leads whose last research attempt failed."""
    result = await db.execute(
        select(Lead).where(Lead.status.in_(["research_failed", "raw"])).limit(100)
    )
    leads = result.scalars().all()
    for lead in leads:
        lead.status = "researching"
    await db.commit()
    return TaskQueued(task_id="batch", message=f"{len(leads)} leads re-queued for research")
