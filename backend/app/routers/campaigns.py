from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.campaign import Campaign
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("")
async def list_campaigns(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Phase 9 stub — schema ready, sending engine not yet implemented."""
    result = await db.execute(select(Campaign).order_by(Campaign.created_at.desc()))
    campaigns = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "status": c.status,
            "sent_count": c.sent_count,
            "open_count": c.open_count,
            "created_at": c.created_at.isoformat(),
        }
        for c in campaigns
    ]
