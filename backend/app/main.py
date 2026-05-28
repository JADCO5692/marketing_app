import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.version import __version__
from app.logging_setup import setup_logging
from app.routers import auth, leads, companies, upload, segments, duplicates, analytics, research, campaigns
from app.routers import admin

logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Application starting — v%s", __version__)

    from app.database import AsyncSessionLocal
    from app.services.settings_service import load_overrides
    async with AsyncSessionLocal() as db:
        try:
            await load_overrides(db)
            logger.info("Settings loaded from database")
        except Exception as exc:
            logger.warning("Could not load settings from DB (migrations pending?): %s", exc)

    yield
    logger.info("Application shutdown")


app = FastAPI(
    title="Marketing Lead Intelligence API",
    description="AI-powered lead enrichment, segmentation, and campaign targeting.",
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_access_log = logging.getLogger("app.access")
_SKIP_PATHS = {"/api/v1/health", "/api/v1/admin/logs"}


@app.middleware("http")
async def request_log_middleware(request: Request, call_next):
    if request.url.path in _SKIP_PATHS:
        return await call_next(request)
    t0 = time.monotonic()
    response = await call_next(request)
    ms = round((time.monotonic() - t0) * 1000)
    _access_log.info(
        "%s %s → %d  (%dms)",
        request.method,
        request.url.path,
        response.status_code,
        ms,
    )
    return response


app.include_router(auth.router,        prefix="/api/v1/auth",        tags=["auth"])
app.include_router(upload.router,      prefix="/api/v1/upload",      tags=["upload"])
app.include_router(leads.router,       prefix="/api/v1/leads",       tags=["leads"])
app.include_router(companies.router,   prefix="/api/v1/companies",   tags=["companies"])
app.include_router(duplicates.router,  prefix="/api/v1/duplicates",  tags=["duplicates"])
app.include_router(segments.router,    prefix="/api/v1/segments",    tags=["segments"])
app.include_router(analytics.router,   prefix="/api/v1/analytics",   tags=["analytics"])
app.include_router(research.router,    prefix="/api/v1/research",    tags=["research"])
app.include_router(campaigns.router,   prefix="/api/v1/campaigns",   tags=["campaigns"])
app.include_router(admin.router,       prefix="/api/v1/admin",       tags=["admin"])


@app.get("/api/v1/version", tags=["system"])
async def get_version():
    return {"version": __version__}


@app.get("/api/v1/health", tags=["system"])
async def health():
    return {"status": "ok"}
