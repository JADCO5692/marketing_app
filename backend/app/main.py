from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.version import __version__
from app.routers import auth, leads, companies, upload, segments, duplicates, analytics, research, campaigns


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


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

app.include_router(auth.router,        prefix="/api/v1/auth",        tags=["auth"])
app.include_router(upload.router,      prefix="/api/v1/upload",      tags=["upload"])
app.include_router(leads.router,       prefix="/api/v1/leads",       tags=["leads"])
app.include_router(companies.router,   prefix="/api/v1/companies",   tags=["companies"])
app.include_router(duplicates.router,  prefix="/api/v1/duplicates",  tags=["duplicates"])
app.include_router(segments.router,    prefix="/api/v1/segments",    tags=["segments"])
app.include_router(analytics.router,   prefix="/api/v1/analytics",   tags=["analytics"])
app.include_router(research.router,    prefix="/api/v1/research",    tags=["research"])
app.include_router(campaigns.router,   prefix="/api/v1/campaigns",   tags=["campaigns"])


@app.get("/api/v1/version", tags=["system"])
async def get_version():
    return {"version": __version__}


@app.get("/api/v1/health", tags=["system"])
async def health():
    return {"status": "ok"}
