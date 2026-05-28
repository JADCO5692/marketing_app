"""
ARQ worker entrypoint.
Start with: arq workers.arq_worker.WorkerSettings
"""
import os
from arq.connections import RedisSettings
from workers.tasks.research_lead import research_lead
from workers.tasks.classify_lead import classify_lead
from workers.tasks.embed_lead import embed_lead


async def startup(ctx: dict) -> None:
    """Load DB settings overrides so get_setting() works in all tasks."""
    from app.database import AsyncSessionLocal
    from app.services.settings_service import load_overrides
    async with AsyncSessionLocal() as db:
        try:
            await load_overrides(db)
        except Exception:
            pass  # DB may not be ready yet; tasks will retry


class WorkerSettings:
    functions = [research_lead, classify_lead, embed_lead]
    on_startup = startup
    redis_settings = RedisSettings.from_dsn(
        os.getenv("REDIS_URL", "redis://localhost:6379/0")
    )
    max_jobs = int(os.getenv("MAX_CONCURRENT_RESEARCH_WORKERS", "4"))
    job_timeout = 300
    keep_result = 3600
    retry_jobs = True
    max_tries = 3
