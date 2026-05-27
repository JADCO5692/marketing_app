import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
import uuid

from app.database import get_db
from app.models.segment import Segment
from app.models.lead import Lead
from app.schemas.segment import SegmentCreate, SegmentUpdate, SegmentResponse, SegmentPreviewResponse
from app.schemas.lead import LeadResponse
from app.schemas.common import PaginatedResponse
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter()


def _build_filter_clause(rules: dict):
    """Translate filter_rules JSON to SQLAlchemy WHERE clauses."""
    clauses = []
    field_map = {
        "status": Lead.status,
        "campaign_type_match": Lead.campaign_type_match,
        "seniority_level": Lead.seniority_level,
        "department": Lead.department,
        "email_deliverability": Lead.email_deliverability,
        "is_decision_maker": Lead.is_decision_maker,
        "budget_authority": Lead.budget_authority,
        "email_verified": Lead.email_verified,
    }
    score_map = {
        "icp_score": Lead.icp_score,
        "intent_score": Lead.intent_score,
        "engagement_readiness": Lead.engagement_readiness,
    }
    for key, value in rules.items():
        if key in score_map:
            col = score_map[key]
            if isinstance(value, dict):
                if ">" in value:
                    clauses.append(col > value[">"])
                if ">=" in value:
                    clauses.append(col >= value[">="])
                if "<" in value:
                    clauses.append(col < value["<"])
                if "<=" in value:
                    clauses.append(col <= value["<="])
            else:
                clauses.append(col == value)
        elif key in field_map:
            col = field_map[key]
            if isinstance(value, list):
                clauses.append(col.in_(value))
            else:
                clauses.append(col == value)
    return clauses


async def _count_segment(db: AsyncSession, rules: dict) -> int:
    clauses = _build_filter_clause(rules)
    q = select(func.count(Lead.id)).where(Lead.status != "invalid")
    if clauses:
        q = q.where(and_(*clauses))
    return (await db.execute(q)).scalar_one()


async def _query_segment(db: AsyncSession, rules: dict, limit: int, offset: int):
    clauses = _build_filter_clause(rules)
    q = select(Lead).where(Lead.status != "invalid")
    if clauses:
        q = q.where(and_(*clauses))
    result = await db.execute(q.order_by(Lead.icp_score.desc().nullslast()).limit(limit).offset(offset))
    return result.scalars().all()


@router.get("", response_model=list[SegmentResponse])
async def list_segments(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Segment).order_by(Segment.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=SegmentResponse, status_code=201)
async def create_segment(
    body: SegmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = await _count_segment(db, body.filter_rules)
    segment = Segment(name=body.name, description=body.description, filter_rules=body.filter_rules, lead_count=count)
    db.add(segment)
    await db.commit()
    await db.refresh(segment)
    return segment


@router.get("/{segment_id}", response_model=SegmentResponse)
async def get_segment(segment_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    segment = await db.get(Segment, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    return segment


@router.get("/{segment_id}/leads", response_model=PaginatedResponse[LeadResponse])
async def segment_leads(
    segment_id: uuid.UUID,
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    segment = await db.get(Segment, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    total = await _count_segment(db, segment.filter_rules)
    leads = await _query_segment(db, segment.filter_rules, limit, offset)
    return PaginatedResponse(items=leads, total=total, limit=limit, offset=offset)


@router.put("/{segment_id}", response_model=SegmentResponse)
async def update_segment(
    segment_id: uuid.UUID,
    body: SegmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    segment = await db.get(Segment, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(segment, field, value)
    if body.filter_rules is not None:
        segment.lead_count = await _count_segment(db, segment.filter_rules)
    await db.commit()
    await db.refresh(segment)
    return segment


@router.delete("/{segment_id}", status_code=204)
async def delete_segment(segment_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    segment = await db.get(Segment, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    await db.delete(segment)
    await db.commit()


@router.post("/{segment_id}/export")
async def export_segment(
    segment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    segment = await db.get(Segment, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    leads = await _query_segment(db, segment.filter_rules, limit=10000, offset=0)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "email", "phone", "job_title", "department",
                     "seniority_level", "icp_score", "intent_score", "campaign_type_match"])
    for lead in leads:
        writer.writerow([lead.name, lead.email, lead.phone, lead.job_title,
                         lead.department, lead.seniority_level, lead.icp_score,
                         lead.intent_score, lead.campaign_type_match])
    output.seek(0)
    filename = f"segment_{segment.name.replace(' ', '_')}.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/preview", response_model=SegmentPreviewResponse)
async def preview_segment(
    body: SegmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = await _count_segment(db, body.filter_rules)
    sample = await _query_segment(db, body.filter_rules, limit=5, offset=0)
    return SegmentPreviewResponse(
        lead_count=count,
        sample_leads=[{"name": l.name, "email": l.email, "icp_score": l.icp_score} for l in sample],
    )
