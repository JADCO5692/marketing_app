"""
ARQ worker entrypoint.
Start with: arq workers.arq_worker.WorkerSettings
"""
import os
from arq.connections import RedisSettings
from workers.tasks.research_lead import research_lead
from workers.tasks.classify_lead import classify_lead
from workers.tasks.embed_lead import embed_lead


class WorkerSettings:
    functions = [research_lead, classify_lead, embed_lead]
    redis_settings = RedisSettings.from_dsn(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    max_jobs = int(os.getenv("MAX_CONCURRENT_RESEARCH_WORKERS", "4"))
    job_timeout = 300        # 5 min per job
    keep_result = 3600       # keep result in Redis for 1h
    retry_jobs = True
    max_tries = 3
