"""
Settings service — DB-first with env-var fallback.

`get_setting(key)` is synchronous and safe to call anywhere.
Call `load_overrides(db)` at app startup and after any write to populate
the in-memory cache so services don't need a DB session at call-time.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings as env_settings

# In-memory override cache populated at startup and on each write
_overrides: dict[str, str] = {}

SENSITIVE_KEYS = {
    "CLAUDE_API_KEY", "OPENAI_API_KEY", "SERPER_API_KEY",
    "HUNTER_API_KEY", "TAVILY_API_KEY", "APOLLO_API_KEY", "GEMINI_API_KEY",
}

SETTINGS_META = [
    {
        "group": "AI Models",
        "items": [
            {"key": "CLAUDE_API_KEY",  "label": "Claude API Key",  "type": "secret",
             "description": "Anthropic API key — used for research synthesis and lead classification. Get one at console.anthropic.com."},
            {"key": "CLAUDE_MODEL",    "label": "Claude Model",    "type": "text",
             "description": "Model ID to use (e.g. claude-sonnet-4-6). Defaults to the value in .env."},
            {"key": "OPENAI_API_KEY",  "label": "OpenAI API Key",  "type": "secret",
             "description": "Used for text-embedding-3-small to generate lead embeddings for semantic deduplication."},
            {"key": "GEMINI_API_KEY",  "label": "Gemini API Key",  "type": "secret",
             "description": "Google Gemini API key — optional alternative AI provider. Get one at aistudio.google.com."},
        ],
    },
    {
        "group": "Research APIs",
        "items": [
            {"key": "SERPER_API_KEY",  "label": "Serper API Key",  "type": "secret",
             "description": "Google Search via serper.dev — free 2,500 queries/mo. Used for company research."},
            {"key": "HUNTER_API_KEY",  "label": "Hunter.io API Key","type": "secret",
             "description": "Email verification and discovery — free 25 verifications/mo at hunter.io."},
            {"key": "TAVILY_API_KEY",  "label": "Tavily API Key",   "type": "secret",
             "description": "AI-optimised search (optional alternative to Serper) — free tier available at tavily.com."},
            {"key": "APOLLO_API_KEY",  "label": "Apollo API Key",   "type": "secret",
             "description": "Full contact + company enrichment (optional) — free tier at apollo.io."},
        ],
    },
    {
        "group": "Deduplication",
        "items": [
            {"key": "DEDUP_AUTO_MERGE_THRESHOLD",  "label": "Auto-merge Threshold",  "type": "number",
             "description": "Cosine similarity (0–1) above which two leads are automatically merged. Default: 0.97."},
            {"key": "DEDUP_REVIEW_THRESHOLD",      "label": "Review Threshold",       "type": "number",
             "description": "Cosine similarity above which a pair is flagged for manual review. Default: 0.92."},
        ],
    },
    {
        "group": "Feature Flags",
        "items": [
            {"key": "RESEARCH_ENABLED",               "label": "Research Enabled",        "type": "bool",
             "description": "Globally enable or disable the AI research pipeline."},
            {"key": "MAX_CONCURRENT_RESEARCH_WORKERS","label": "Max Research Workers",    "type": "number",
             "description": "Maximum concurrent research jobs in the ARQ worker. Default: 4."},
        ],
    },
]


def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """Return DB override if set, else env var, else default."""
    if key in _overrides and _overrides[key]:
        return _overrides[key]
    val = getattr(env_settings, key, None)
    if val is not None:
        return str(val)
    return default


def _mask(value: str) -> str:
    if len(value) <= 4:
        return "●" * len(value)
    return "●" * (len(value) - 4) + value[-4:]


async def load_overrides(db: AsyncSession) -> None:
    from app.models.app_setting import AppSetting
    result = await db.execute(select(AppSetting))
    _overrides.clear()
    for row in result.scalars().all():
        if row.value:
            _overrides[row.key] = row.value


async def list_settings(db: AsyncSession) -> list[dict]:
    from app.models.app_setting import AppSetting
    result = await db.execute(select(AppSetting))
    db_rows = {r.key: r for r in result.scalars().all()}

    out = []
    for group in SETTINGS_META:
        for item in group["items"]:
            key = item["key"]
            db_row = db_rows.get(key)
            env_val = str(getattr(env_settings, key, "") or "")

            # Determine display source and value
            if db_row and db_row.value:
                source = "db"
                display = _mask(db_row.value) if item["type"] == "secret" else db_row.value
            elif env_val:
                source = "env"
                display = _mask(env_val) if item["type"] == "secret" else env_val
            else:
                source = "unset"
                display = ""

            out.append({
                **item,
                "group": group["group"],
                "value": display,
                "source": source,
                "updated_at": db_row.updated_at.isoformat() if db_row else None,
            })
    return out


async def upsert_setting(db: AsyncSession, key: str, value: str) -> None:
    from app.models.app_setting import AppSetting
    from datetime import datetime, timezone
    result = await db.execute(select(AppSetting).where(AppSetting.key == key))
    row = result.scalar_one_or_none()
    if row:
        row.value = value
        row.updated_at = datetime.now(timezone.utc)
    else:
        db.add(AppSetting(key=key, value=value))
    await db.commit()
    _overrides[key] = value


async def delete_setting(db: AsyncSession, key: str) -> None:
    from app.models.app_setting import AppSetting
    result = await db.execute(select(AppSetting).where(AppSetting.key == key))
    row = result.scalar_one_or_none()
    if row:
        await db.delete(row)
        await db.commit()
    _overrides.pop(key, None)
