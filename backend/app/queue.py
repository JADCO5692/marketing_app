"""Shared ARQ queue pool. Call get_queue() to enqueue tasks."""
from arq import create_pool
from arq.connections import RedisSettings
from app.config import settings

_pool = None


async def get_queue():
    global _pool
    if _pool is None:
        _pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    return _pool


async def close_queue():
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None
