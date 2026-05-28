from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.services import settings_service
from app.logging_setup import get_logs

router = APIRouter()


class SettingWrite(BaseModel):
    value: str


# ── Settings ──────────────────────────────────────────────────────────────────

@router.get("/settings")
async def list_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await settings_service.list_settings(db)


@router.put("/settings/{key}")
async def update_setting(
    key: str,
    body: SettingWrite,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate key is in known settings
    known_keys = {
        item["key"]
        for group in settings_service.SETTINGS_META
        for item in group["items"]
    }
    if key not in known_keys:
        raise HTTPException(status_code=400, detail=f"Unknown setting key: {key}")
    await settings_service.upsert_setting(db, key, body.value.strip())
    return {"key": key, "status": "saved"}


@router.delete("/settings/{key}")
async def reset_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await settings_service.delete_setting(db, key)
    return {"key": key, "status": "reset to env default"}


# ── App Logs ──────────────────────────────────────────────────────────────────

@router.get("/logs")
async def app_logs(
    level: Optional[str] = None,
    logger: Optional[str] = None,
    limit: int = 200,
    current_user: User = Depends(get_current_user),
):
    return get_logs(level=level, logger_filter=logger, limit=min(limit, 500))
