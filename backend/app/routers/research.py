from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from app.database import get_db
from app.models.lead import Lead
from app.models.research_log import ResearchLog
from app.schemas.common import PaginatedResponse, TaskQueued
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter()


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
