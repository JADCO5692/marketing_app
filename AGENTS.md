# AGENTS.md — `marketing_project`

Source files are authoritative for exact lines. This file is non-derivable context only.

---

## 0. Agent Instructions (READ THIS FIRST)

This file is the shared context for **all AI agents** working on this project (Claude Code, Codex, etc.). Every agent MUST follow these rules:

### Process

1. **Read this file first** before making any changes.
2. **Check the Feature Log (§0.2)** to see what's done, in progress, and planned.
3. **Update the Feature Log** when you start or finish a feature. Mark `in_progress` when you begin, `done` when complete.
4. **Document changes** in the Feature Log with version, date, and a brief description.
5. **Bump the version** in `backend/app/version.py` on every schema/behaviour change. Follow the versioning policy in §18 — wrong bump type is a mistake that stays in git history.
6. **Do NOT duplicate logic.** Check if a service/function already exists before writing a new one. The research pipeline, AI classifier, and duplicate detector are shared — use them.
7. **Source files are authoritative.** This file provides context and intent. If this file disagrees with the code, the code wins — update this file.
8. **No mixing of concerns.** `marketing_app/` is source code only. `other_items_to_install/` is for Docker Compose, nginx config, environment templates, and any tool that does not require code maintenance.
9. **Always restart containers after backend changes** (see §0.3 restart matrix). Changes to Python files are NOT automatically picked up — uvicorn `--reload` only works for syntax-level reloads, not for in-memory caches like `SETTINGS_META` or `_overrides`. Failure to restart means the old code keeps running and changes appear to have no effect.

### Style Rules

- UTC everywhere internally. Display in user's local timezone on the frontend.
- All AI calls go through `services/ai_client.py` — never call Claude/OpenAI directly from a route.
- All research calls go through `services/research/` — never call Serper/Hunter/Playwright directly from a route.
- No hardcoded API keys anywhere. All secrets via environment variables loaded from `.env`.
- Python: `snake_case`. React/TypeScript: `camelCase` for variables, `PascalCase` for components.
- Database migrations via Alembic only — never alter tables manually.
- Every new API route must have a corresponding Pydantic request/response schema.
- Every background task must be an ARQ worker function, never a FastAPI background task (those die with the request).

### FastAPI Development Standards (MANDATORY)

| Do | Do NOT |
|---|---|
| Use `async def` for all route handlers | Use sync `def` in route handlers (blocks event loop) |
| Use Pydantic v2 models for request/response | Return raw dicts from routes |
| Use `Depends()` for shared dependencies (DB session, auth) | Import `db` directly in routes |
| Use `APIRouter` with prefix + tags per module | Put all routes in `main.py` |
| Use `HTTPException` with explicit status codes | Raise generic `Exception` |
| Validate all CSV input at parse time | Trust raw CSV data downstream |
| Use `Optional[X]` for nullable fields | Use `X | None` (Python 3.9 compat) |

### React / TypeScript Standards (MANDATORY)

| Do | Do NOT |
|---|---|
| Functional components + hooks only | Class components |
| `zustand` for global state | Redux or Context for simple state |
| `react-query` (TanStack Query) for server state | Manual `useEffect` + `fetch` for data |
| `tailwindcss` + `shadcn/ui` for UI | Custom CSS or inline styles |
| `recharts` for all charts | Other charting libraries |
| Typed API client via `openapi-typescript` | Manual `fetch` with untyped responses |
| Error boundaries per major page section | One global error boundary |

### Metric Tooltips (§0.3) — MANDATORY

Every KPI label added to the UI **must** carry a `data-tip="KEY"` attribute that connects to the central tooltip dictionary at `frontend/src/lib/kpi-tips.ts`.

**Rule for every new KPI:**
1. Add the key to `kpi-tips.ts` first: `{ title: 'Display Name', body: 'Plain explanation.' }`
2. Add `data-tip="your_key"` to the label element.
3. `body` may use `**bold**` for emphasis. Keep it one or two sentences.

**Existing covered keys:** *(none yet — add as features land)*

### Feature Log (§0.2)

Update this table when starting or completing features. Date format: `YYYY-MM-DD`.

| Version | Date | Feature | Status | Notes |
|---------|------|---------|--------|-------|
| 0.1.0 | 2026-05-27 | Full v0.1.0 foundation | done | Docker Compose + nginx; FastAPI with JWT auth, CSV upload, leads/companies/duplicates/segments/analytics/research routers; ARQ workers (research, embed, classify); pgvector semantic dedup; Claude synthesis; React frontend with all 8 pages (Upload, Leads, Companies, Duplicates, Research, Segments, KPI Dashboard, Campaigns stub); Alembic async migrations |
| 0.1.1 | 2026-05-28 | Research pipeline bug fixes | done | Fixed 7 bugs blocking end-to-end research: (1) trigger_research route was a stub — never enqueued ARQ task; (2) ARQ worker never loaded DB settings (`on_startup` hook missing), so API keys were invisible to the worker; (3) wrong AI package (`google-generativeai` deprecated → `google-genai>=1.0.0`); (4) Gemini model `gemini-2.0-flash` discontinued → `gemini-2.5-flash`; (5) zero-width space (U+200B) contamination in stored API keys — added `_sanitize()` in settings_service; (6) synthesizer silently swallowed all exceptions — added logger.error; (7) app logs slicing bug returned oldest entries not newest. Also added sonner toast notifications for research/delete actions and real-time request logging middleware. |
| 0.2.0 | 2026-05-28 | Lead management + multi-provider AI | done | POST /leads (manual lead creation with company auto-resolve); DELETE /leads (delete all with confirmation); Gemini API key added to Settings UI and SETTINGS_META; ai_client.py rewritten to auto-select provider (Claude → Gemini → OpenAI) from DB settings; migration 20260528_020 adds `app_settings` table. |
| 0.2.1 | 2026-05-28 | Research log improvements | done | Migration 20260528_030 adds `duration_ms` to `research_logs`. Each research step (playwright/serper/hunter/synthesis) is individually timed via `_timed()` wrapper in research_lead.py. Research page updated: Duration column (ms/s), full datetime (date + time) in Created At, source filter includes gemini/claude/openai/ai. |
| 0.3.0 | 2026-05-28 | Leads page UX — checkbox delete + column picker | done | Checkbox column added to Leads table for multi-select; "Delete N selected" button with confirmation modal; ColumnPicker dropdown lists all 20 Lead model fields (phone, LinkedIn, department, seniority, decision maker, budget authority, campaign fit, email verified, deliverability, email type, source file, created at, plus defaults); selections persisted to `localStorage` under key `leads:visibleCols` so they survive page refresh. |
| 0.4.1 | 2026-05-28 | Configurable page size on Leads table | done | "Rows per page" selector (10 / 25 / 50 / 100 / 200) added to the Leads pagination bar. Selection persisted to `localStorage` under `leads:pageSize`. Resets to page 1 on change. Total lead count always shown. UI-only change — no backend or schema changes. |
| 0.5.3 | 2026-05-29 | Address fields on leads | done | Migration 20260529_060 adds street_address, city, state, country, zip_code to leads table. LeadResponse schema exposes all five. Upload router normalises variant spellings (zip/postal_code/postcode → zip_code; address/street/street1/address1 → street_address) before mapping. ALL_COLUMNS in Leads.tsx extended with the 5 address fields under Contact group; drawer Contact section shows them with "—" when absent. |
| 0.5.2 | 2026-05-29 | Always-show drawer fields + DrawerArrayField | done | DrawerSection no longer hides when fields are empty — all fields render with "— " for null values so users can see the full schema at all times. New DrawerArrayField component handles 6 display variants (bullet, tag, badge-success, badge-danger, arrow, check). Signal Intelligence section always renders all 8 signal categories. Campaign Recommendations always renders. Column picker now groups columns with section headers and scrolls. |
| 0.5.1 | 2026-05-29 | Expose all enrichment fields in Leads UI | done | ALL_COLUMNS expanded to 36 entries across 7 groups (Contact, Company, Role, Scores, Intent, Outreach, Intelligence, Meta). Column picker now shows groups with headers and scrolls. renderCell handles SCORE_KEYS (right-aligned, color-coded), ARRAY_KEYS (truncated "a, b +N"), and BLOB_KEYS ("in sidebar"). Score card grid extended to 6 cards (2 rows: ICP/Intent/Engage + Engage%/Resp%/CampFit). Drawer rewritten with Role & Influence section (role_influence, personality_style, linkedin_activity_level), Intent section (buying_stage, buying_signals with ↑ icon, risk_flags with ⚠ icon), Outreach section (personalization_tags, outreach_angles, likely_kpis, likely_pain_points), Campaign Recommendations section (channels, hooks, value_props, CTA, urgency), Signal Intelligence section (all 8 signal arrays rendered by category). |
| 0.5.0 | 2026-05-28 | Full GTM enrichment schema + new research prompt | done | Migration 20260528_050 adds 15 new lead columns (engagement_likelihood, response_probability, campaign_fit_score, role_influence, personality_style, linkedin_activity_level, buying_stage, preferred_campaign_type, likely_pain_points, likely_kpis, outreach_angles, buying_signals, risk_flags, campaign_recommendations JSONB, signals JSONB) and 17 new company columns (business_model, growth_stage, multi_location, operational_complexity, supply_chain_complexity, expansion_signals, recent_business_events, likely_business_goals, procurement_maturity, vendor_dependency_likelihood, tools_detected, brand_maturity_score, technology_maturity, digital_maturity, estimated_monthly_traffic, competitive_intelligence JSONB, marketing_signals JSONB). Research prompt replaced with full B2B revenue intelligence engine prompt extracting GTM signals, buying intent, campaign recommendations, and signal arrays. Worker maps all new fields; legacy fields (campaign_type_match, pain_point_clusters) kept in sync. Upload page now shows unmapped columns in an amber panel after success so new fields can be identified. |
| 0.4.4 | 2026-05-28 | Configurable research prompt template | done | New "Research" group in Settings with a full-width textarea. Default prompt is pre-filled for packaging/box supply B2B context (ICP scoring for ecommerce/manufacturing/retail, pain points around cost-per-unit and lead time). Synthesizer now reads RESEARCH_PROMPT_TEMPLATE from DB settings at call time — changes in the UI take effect on the next research job without a restart. Falls back to the hardcoded default if unset. |
| 0.4.3 | 2026-05-28 | Fix lead delete (hard delete) | done | DELETE /leads/{id} was soft-deleting (setting status="invalid") so records never disappeared from the list. Changed to `await db.delete(lead)` (hard delete), consistent with the delete-all endpoint. |
| 0.4.0 | 2026-05-28 | Research queue management — cancel / pause / resume | done | Migration 20260528_040 adds `arq_job_id` to `leads`. Job ID stored on enqueue so it can be aborted. New endpoints: GET /research/queue (live queue with paused flag), POST /leads/{id}/cancel-research, POST /research/cancel-all, POST /research/pause, POST /research/resume. Pause uses `RESEARCH_PAUSED` key in `app_settings`; worker checks this fresh from DB at task start (bypasses in-memory cache). Resume re-enqueues all "researching" leads. QueuePanel component auto-polls every 2.5 s; turns grey when paused; shows Pause All / Resume toggle and Cancel All button. Task guards against race condition: re-fetches lead status after API calls complete and aborts write if lead was cancelled. |

---

## 0.3. Service Operations (start / stop / migrate)

All commands run from `other_items_to_install/`.

### Prerequisites (first time only)

```bash
# Install Colima + Docker CLI (macOS, Apple Silicon)
brew install colima docker docker-compose

# Start Colima VM (4 CPU, 6 GB RAM, 60 GB disk)
colima start --cpu 4 --memory 6 --disk 60

# Verify Docker is reachable
docker info
```

### Start (development — hot reload on all services)

```bash
cd other_items_to_install

# 1. Start Colima VM (if not already running)
colima start

# 2. Build images (first time, or after requirements.txt / Dockerfile changes)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

# 3. Start all 5 services in the background
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 4. Run DB migrations (only needed after first start or new migration files)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec api alembic upgrade head

# 5. (First time only) Create an admin account
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"YourPassword","full_name":"Admin"}'
```

**Access points (dev mode):**
| Service  | URL |
|----------|-----|
| Frontend | http://localhost:3001 |
| API      | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| Postgres | localhost:5432 (user: marketing_user, db: marketing_db) |
| Redis    | localhost:6379 |

### Graceful stop

```bash
cd other_items_to_install

# Stop all containers but keep volumes (data preserved)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml stop

# Stop Colima VM (frees RAM/CPU, data still in Colima disk)
colima stop
```

### Destroy (wipe everything including DB data)

```bash
cd other_items_to_install

# Remove containers AND volumes (irreversible — deletes all lead data)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v

colima stop
```

### Useful day-to-day commands

```bash
# View live logs from all services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

# View logs for a single service (api | worker | frontend | postgres | redis)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f api

# Check service status
docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps

# Restart a single service after code change
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart api

# Run a new Alembic migration (after adding migration file)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec api alembic upgrade head

# Open a psql shell
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec postgres \
  psql -U marketing_user -d marketing_db
```

> **Note:** In dev mode the backend volume-mounts `marketing_app/backend` so Python file changes are
> picked up automatically by uvicorn `--reload`. `requirements.txt` changes require a `docker-compose build api` + `up -d --force-recreate api`.

### After making changes — restart matrix (MANDATORY)

Every time you edit backend Python files, run the corresponding restart command before declaring the task done. Not doing this is the #1 cause of "my change has no effect" bugs.

| What you changed | Command to run |
|---|---|
| `app/services/settings_service.py` (SETTINGS_META, prompts, descriptions) | `restart api` |
| `app/routers/` or `app/services/` (any route or service logic) | `restart api` |
| `app/models/` (SQLAlchemy models) | `restart api` + `restart worker` |
| `workers/tasks/` (ARQ task logic) | `restart worker` |
| `workers/tasks/` + any model/service it imports | `restart api` + `restart worker` |
| New Alembic migration | `exec api alembic upgrade head` → `restart api` → `restart worker` |
| `requirements.txt` or `Dockerfile` | `build api` → `up -d --force-recreate api` |
| Frontend `.tsx` / `.ts` files | **No restart needed** — Vite hot-reloads automatically |

```bash
# Restart API only
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart api

# Restart worker only
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart worker

# Restart both (safest default after any backend change)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart api worker

# Run migration then restart both
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec api alembic upgrade head \
  && docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart api worker
```

**Rule of thumb:** when in doubt, `restart api worker`. It takes 3 seconds and costs nothing.

---

## 1. North Star — build in this order, never skip ahead

1. **Infrastructure** — Docker Compose, Postgres + pgvector, Redis, FastAPI skeleton, React skeleton, Alembic migrations
2. **Ingestion** — CSV upload, parse, validate, store raw leads
3. **Deduplication** — exact match (email/phone) + fuzzy/semantic match (pgvector embeddings)
4. **Research pipeline** — async ARQ workers: website scrape → Google search → email verify → Claude synthesis → structured KPI enrichment
5. **AI Classification** — industry, sub-industry, region, business type, ICP score, intent score, engagement readiness
6. **Grouping & Segmentation** — rule-based filters + AI-suggested clusters on any KPI combination
7. **KPI Dashboard** — charts and breakdowns across all enrichment dimensions
8. **Campaign preparation** — segment export, personalisation tag review, email template builder
9. **Email automation** — sending engine, open/click tracking, unsubscribe, campaign analytics

---

## 2. Identity

| | |
|---|---|
| Project name | `marketing_project` |
| Version | `0.4.1` — see §18 for bump rules. Single source of truth: `backend/app/version.py` |
| Backend | FastAPI (Python 3.12) + ARQ workers |
| Frontend | React 18 + Vite + TypeScript + Tailwind CSS + shadcn/ui |
| Database | PostgreSQL 16 + pgvector extension |
| Queue | Redis 7 (task queue + result cache) |
| Container | Docker Compose (5 services: api, worker, frontend, postgres, redis) |
| Source code root | `marketing_app/` |
| Non-code installs | `other_items_to_install/` (Docker Compose, nginx, `.env.example`, tool configs) |
| TZ | UTC internally. Frontend displays in user timezone. |
| Auth | JWT (FastAPI-Users library) |

---

## 3. Folder Structure

```
marketing_project/
├── marketing_app/AGENTS.md          ← this file (project source of truth)
│
├── marketing_app/                   ← ALL source code lives here
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py              ← FastAPI app factory
│   │   │   ├── version.py           ← single version string
│   │   │   ├── config.py            ← settings via pydantic-settings (.env)
│   │   │   ├── database.py          ← SQLAlchemy async engine + session
│   │   │   ├── models/              ← SQLAlchemy ORM models
│   │   │   │   ├── lead.py
│   │   │   │   ├── company.py
│   │   │   │   ├── research_log.py
│   │   │   │   ├── segment.py
│   │   │   │   └── campaign.py      ← schema-ready, not yet active
│   │   │   ├── schemas/             ← Pydantic v2 request/response models
│   │   │   ├── routers/             ← APIRouter modules (one per domain)
│   │   │   │   ├── leads.py
│   │   │   │   ├── companies.py
│   │   │   │   ├── upload.py
│   │   │   │   ├── research.py
│   │   │   │   ├── segments.py
│   │   │   │   ├── duplicates.py
│   │   │   │   └── campaigns.py     ← stub only until Phase 9
│   │   │   └── services/
│   │   │       ├── ai_client.py     ← single AI call gateway (Claude + others)
│   │   │       ├── classifier.py    ← AI classification pipeline
│   │   │       ├── deduplicator.py  ← exact + semantic duplicate detection
│   │   │       ├── embeddings.py    ← generate + store pgvector embeddings
│   │   │       └── research/
│   │   │           ├── __init__.py
│   │   │           ├── scraper.py   ← Playwright website scraper
│   │   │           ├── search.py    ← Serper Google search wrapper
│   │   │           ├── email_verify.py ← Hunter.io email verification
│   │   │           └── synthesizer.py  ← Claude: merge all research → KPIs
│   │   ├── workers/
│   │   │   ├── arq_worker.py        ← ARQ worker entrypoint + settings
│   │   │   └── tasks/
│   │   │       ├── research_lead.py ← full research pipeline per lead
│   │   │       ├── classify_lead.py ← AI classification task
│   │   │       └── embed_lead.py    ← embedding generation task
│   │   ├── migrations/              ← Alembic migration scripts
│   │   │   ├── env.py
│   │   │   └── versions/
│   │   ├── alembic.ini
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── frontend/
│       ├── src/
│       │   ├── main.tsx
│       │   ├── App.tsx
│       │   ├── lib/
│       │   │   ├── api.ts           ← typed API client (from openapi spec)
│       │   │   ├── kpi-tips.ts      ← central KPI tooltip dictionary
│       │   │   └── utils.ts
│       │   ├── store/               ← zustand stores
│       │   ├── components/          ← shadcn/ui + custom components
│       │   ├── pages/
│       │   │   ├── Upload.tsx
│       │   │   ├── Leads.tsx
│       │   │   ├── Companies.tsx
│       │   │   ├── Duplicates.tsx
│       │   │   ├── Research.tsx
│       │   │   ├── Segments.tsx
│       │   │   ├── KpiDashboard.tsx
│       │   │   └── Campaigns.tsx    ← stub until Phase 9
│       │   └── hooks/
│       ├── public/
│       ├── index.html
│       ├── vite.config.ts
│       ├── tailwind.config.ts
│       ├── tsconfig.json
│       ├── package.json
│       └── Dockerfile
│
└── other_items_to_install/          ← no source code here
    ├── docker-compose.yml           ← orchestrates all 5 services
    ├── docker-compose.dev.yml       ← dev overrides (hot reload, port exposure)
    ├── nginx/
    │   └── nginx.conf               ← reverse proxy for frontend + API
    ├── postgres/
    │   └── init.sql                 ← CREATE EXTENSION vector; initial setup
    └── .env.example                 ← all required env vars with descriptions
```

---

## 4. Services (Docker Compose)

| Service | Image | Port | Role |
|---|---|---|---|
| `api` | `./marketing_app/backend` | `8000` | FastAPI REST API |
| `worker` | `./marketing_app/backend` | — | ARQ background worker (same image, different CMD) |
| `frontend` | `./marketing_app/frontend` | `3000` | React Vite dev / nginx prod |
| `postgres` | `pgvector/pgvector:pg16` | `5432` | Primary database |
| `redis` | `redis:7-alpine` | `6379` | ARQ queue + result cache |

All services on an internal Docker network `mkt_net`. Only `api` and `frontend` expose ports to host.

---

## 5. Database Schema

### `companies` table
Normalised company entity. One company can have many leads.

| Column | Type | Notes |
|---|---|---|
| `id` | `UUID PK` | |
| `name` | `TEXT NOT NULL` | Canonical company name |
| `domain` | `TEXT UNIQUE` | Primary domain (used for dedup + research) |
| `industry` | `TEXT` | AI-classified |
| `sub_industry` | `TEXT` | AI-classified |
| `business_model` | `TEXT` | e.g. "SaaS", "Marketplace", "Services" |
| `business_type` | `TEXT` | B2B / B2C / B2B2C / D2C / Marketplace |
| `company_size` | `TEXT` | Startup / SME / Mid-market / Enterprise |
| `growth_stage` | `TEXT` | Early / Growth / Scaling / Mature / Declining |
| `headcount_range` | `TEXT` | e.g. "50–200" |
| `revenue_range` | `TEXT` | e.g. "$1M–$10M" |
| `funding_stage` | `TEXT` | Bootstrap / Seed / Series A / Series B / Series C+ / Public / Unknown |
| `years_operating` | `INT` | Derived from founding year |
| `region` | `TEXT` | Continent-level |
| `country` | `TEXT` | |
| `city` | `TEXT` | |
| `timezone` | `TEXT` | IANA tz string |
| `multi_location` | `BOOL` | AI-inferred — has offices in multiple locations |
| `hiring_velocity` | `TEXT` | High / Medium / Low / None |
| `operational_complexity` | `TEXT` | Low / Medium / High |
| `supply_chain_complexity` | `TEXT` | Low / Medium / High |
| `procurement_maturity` | `TEXT` | Low / Medium / High |
| `vendor_dependency_likelihood` | `TEXT` | Low / Medium / High |
| `technology_maturity` | `TEXT` | Low / Medium / High |
| `digital_maturity` | `TEXT` | Low / Medium / High |
| `expansion_signals` | `TEXT[]` | AI-detected expansion indicators |
| `recent_business_events` | `TEXT[]` | Recent news, launches, hires, funding |
| `likely_business_goals` | `TEXT[]` | AI-inferred strategic goals |
| `tech_stack` | `TEXT[]` | Tools confirmed |
| `tools_detected` | `TEXT[]` | All tools detected (broader than tech_stack) |
| `pain_points` | `TEXT[]` | AI-inferred pain points |
| `website_quality_score` | `FLOAT` | 0–10 |
| `social_presence_score` | `FLOAT` | 0–10 |
| `brand_maturity_score` | `FLOAT` | 0–10 |
| `traffic_estimate` | `TEXT` | Legacy field |
| `estimated_monthly_traffic` | `TEXT` | e.g. "<10K/mo" |
| `recent_news` | `JSONB` | Top 3 news snippets from research |
| `competitive_intelligence` | `JSONB` | competitors_mentioned, current_vendors, switch signals |
| `marketing_signals` | `JSONB` | active_ads, seo_maturity, content_activity, social_level |
| `last_researched_at` | `TIMESTAMPTZ` | |
| `research_status` | `TEXT` | pending / in_progress / done / failed |
| `created_at` | `TIMESTAMPTZ` | |
| `updated_at` | `TIMESTAMPTZ` | |

### `leads` table
Individual contact associated with a company.

| Column | Type | Notes |
|---|---|---|
| `id` | `UUID PK` | |
| `company_id` | `UUID FK → companies` | Nullable until company is resolved |
| `name` | `TEXT` | |
| `email` | `TEXT` | |
| `email_verified` | `BOOL` | Hunter.io result |
| `email_type` | `TEXT` | personal / generic / role-based |
| `email_deliverability` | `TEXT` | deliverable / risky / undeliverable |
| `phone` | `TEXT` | |
| `linkedin_url` | `TEXT` | |
| `street_address` | `TEXT` | From CSV (variants: address, street, street1, address1) |
| `city` | `VARCHAR(100)` | From CSV or AI research |
| `state` | `VARCHAR(100)` | From CSV or AI research |
| `country` | `VARCHAR(100)` | From CSV or AI research |
| `zip_code` | `VARCHAR(20)` | From CSV (variants: zip, postal_code, postcode) |
| `job_title` | `TEXT` | Raw title from CSV |
| `department` | `TEXT` | AI-normalised (Sales / Engineering / Marketing / Finance / C-Suite / etc.) |
| `seniority_level` | `TEXT` | C-Suite / VP / Director / Manager / IC |
| `is_decision_maker` | `BOOL` | AI-inferred from title + seniority |
| `budget_authority` | `BOOL` | AI-inferred |
| `icp_score` | `FLOAT` | 0–100: Ideal Customer Profile fit |
| `intent_score` | `FLOAT` | 0–100: active buying intent signals |
| `engagement_readiness` | `FLOAT` | 0–100: likelihood of responding |
| `engagement_likelihood` | `FLOAT` | 0–100: AI-scored engagement probability |
| `response_probability` | `FLOAT` | 0–100: probability of replying to outreach |
| `campaign_fit_score` | `FLOAT` | 0–100: readiness for immediate outbound campaign |
| `role_influence` | `TEXT` | Low / Medium / High |
| `personality_style` | `TEXT` | Analytical / Operational / Financial / Strategic / Technical / Unknown |
| `linkedin_activity_level` | `TEXT` | High / Medium / Low / Unknown |
| `buying_stage` | `TEXT` | Unaware / Problem Aware / Solution Aware / Vendor Evaluating / Ready to Buy |
| `campaign_type_match` | `TEXT` | Legacy — educational / demo / case_study / offer / nurture |
| `preferred_campaign_type` | `TEXT` | educational / demo / case_study / offer / nurture / comparison |
| `personalization_tags` | `TEXT[]` | e.g. ["scaling fast", "hiring engineers"] |
| `competitive_intel` | `JSONB` | Legacy competitive intel blob |
| `pain_point_clusters` | `TEXT[]` | Legacy — AI-identified pain points |
| `likely_pain_points` | `TEXT[]` | AI-inferred pain points (enrichment v2) |
| `likely_kpis` | `TEXT[]` | KPIs this persona likely owns |
| `outreach_angles` | `TEXT[]` | Specific hooks for personalized outreach |
| `buying_signals` | `TEXT[]` | Detected signals of active buying intent |
| `risk_flags` | `TEXT[]` | Reasons this lead might be low quality or risky |
| `campaign_recommendations` | `JSONB` | Recommended channels, CTAs, hooks, urgency level |
| `signals` | `JSONB` | All signal arrays: growth, buying, operational, tech, logistics, marketing, risk, expansion |
| `raw_csv_data` | `JSONB` | Original CSV row preserved verbatim |
| `embedding` | `vector(1536)` | pgvector: for dedup + clustering |
| `status` | `TEXT` | raw / researching / enriched / duplicate / merged / invalid |
| `arq_job_id` | `TEXT` | ARQ job ID stored on enqueue; cleared when task completes or is cancelled |
| `duplicate_of` | `UUID FK → leads` | Set when status = duplicate |
| `source_file` | `TEXT` | Original CSV filename |
| `source_row` | `INT` | Row number in CSV |
| `created_at` | `TIMESTAMPTZ` | |
| `updated_at` | `TIMESTAMPTZ` | |

**Indexes:**
- `leads(email)` — exact dedup
- `leads(phone)` — exact dedup
- `leads(company_id)` — joins
- `leads(status)` — pipeline filtering
- `leads(icp_score)` — score-based queries
- `leads USING ivfflat (embedding vector_cosine_ops)` — pgvector ANN search

### `research_log` table
Audit trail for every research API call.

| Column | Type | Notes |
|---|---|---|
| `id` | `UUID PK` | |
| `lead_id` | `UUID FK → leads` | |
| `source` | `TEXT` | serper / hunter / playwright / claude |
| `query` | `TEXT` | What was queried |
| `raw_response` | `JSONB` | Full API response |
| `tokens_used` | `INT` | For cost tracking |
| `cost_usd` | `FLOAT` | Estimated cost |
| `duration_ms` | `INT` | Wall-clock time for this step in milliseconds |
| `success` | `BOOL` | |
| `error` | `TEXT` | Error message if failed |
| `created_at` | `TIMESTAMPTZ` | |

### `segments` table
Named subsets of leads defined by KPI filter rules.

| Column | Type | Notes |
|---|---|---|
| `id` | `UUID PK` | |
| `name` | `TEXT NOT NULL` | e.g. "SaaS India Series A Hot" |
| `description` | `TEXT` | |
| `filter_rules` | `JSONB` | e.g. `{"icp_score": {">": 70}, "region": "Asia", "industry": "SaaS"}` |
| `lead_count` | `INT` | Cached, refreshed on demand |
| `created_at` | `TIMESTAMPTZ` | |
| `updated_at` | `TIMESTAMPTZ` | |

### `app_settings` table
Key-value store for runtime configuration overrides. Values set here take priority over `.env` vars. Managed via the Admin → Settings UI or `PUT /admin/settings/{key}`.

| Column | Type | Notes |
|---|---|---|
| `key` | `TEXT PK` | Setting key (e.g. `GEMINI_API_KEY`, `RESEARCH_PAUSED`) |
| `value` | `TEXT` | Stored value; sensitive keys (API keys) are masked in the Settings UI |
| `updated_at` | `TIMESTAMPTZ` | |

**Special runtime keys:**

| Key | Effect |
|---|---|
| `RESEARCH_PAUSED` | `"true"` → worker skips new tasks, leads stay as `researching`; cleared on resume |
| `CLAUDE_API_KEY` / `GEMINI_API_KEY` / `OPENAI_API_KEY` | Overrides `.env` value; `ai_client.py` reads from DB on every call |
| `RESEARCH_ENABLED` | `"false"` → research pipeline globally disabled |

### `campaigns` table
Schema present from day 1, not active until Phase 9.

| Column | Type | Notes |
|---|---|---|
| `id` | `UUID PK` | |
| `segment_id` | `UUID FK → segments` | |
| `name` | `TEXT` | |
| `subject_template` | `TEXT` | Handlebars/Jinja template |
| `body_template` | `TEXT` | HTML template with personalisation slots |
| `status` | `TEXT` | draft / scheduled / sending / sent / paused |
| `scheduled_at` | `TIMESTAMPTZ` | |
| `sent_count` | `INT` | |
| `open_count` | `INT` | |
| `click_count` | `INT` | |
| `bounce_count` | `INT` | |
| `created_at` | `TIMESTAMPTZ` | |

---

## 6. KPI Taxonomy

Every lead/company is enriched with structured KPIs. These drive segmentation and campaign targeting.

### Company-Level KPIs

```
Identity               Size Signals           Financial               Digital Presence
────────               ────────────           ─────────               ────────────────
industry               headcount_range        funding_stage           website_quality_score
sub_industry           office_locations       revenue_range           social_presence_score
business_type          years_operating        funding_recency         tech_stack[]
region / country       hiring_velocity        investors               traffic_estimate
city / timezone        remote vs onsite       growth_signals          mobile_first?
```

### Lead-Level KPIs

```
Contact Quality        Seniority              Engagement Potential
───────────────        ─────────              ────────────────────
email_verified         job_title              is_decision_maker
email_type             seniority_level        budget_authority
email_deliverability   department             campaign_type_match
linkedin_found         reporting_level        personalization_tags[]
phone_valid            org_chart_position     pain_point_clusters[]
```

### AI-Derived KPIs (Claude synthesizes from all research sources)

```
icp_score (0–100)             — how well they match the ideal customer profile
intent_score (0–100)          — signals of active buying intent (news, hiring, tools)
engagement_readiness (0–100)  — likelihood of responding to a cold email
campaign_type_match           — educational / demo / case_study / offer / nurture
personalization_tags[]        — ["scaling fast", "hiring engineers", "new CTO"]
competitive_intel             — tools currently in use, alternatives evaluated
pain_point_clusters[]         — ["manual reporting", "team coordination"]
```

### Segmentation Axes (the 9 dimensions for campaign targeting)

```
Axis 1: Industry + Sub-industry
Axis 2: Region + Country + Timezone
Axis 3: Company Size (SME / Mid-market / Enterprise)
Axis 4: Funding Stage (Bootstrap / Seed / Series A / Series B / Series C+ / Public)
Axis 5: ICP Score bracket (Cold <40 / Warm 40–70 / Hot >70)
Axis 6: Tech Stack category (No-code / Legacy / Modern SaaS / Mixed)
Axis 7: Engagement Readiness bracket
Axis 8: Decision Maker present (Y/N)
Axis 9: Intent Signal strength (Low / Medium / High)
```

---

## 7. Research Pipeline (per lead — async ARQ worker)

```
Step 1: Website Scrape (Playwright)
        → company description, product/service list, contact page, tech stack hints
        Cost: free (your compute)

Step 2: Google Search via Serper
        → recent news, funding announcements, job postings, key people
        Cost: ~$0.001/lead

Step 3: Email Verification via Hunter.io
        → deliverability status, email type, MX record check
        Cost: ~$0.05/lead (free tier: 25/mo)

Step 4: Claude Synthesis (claude-sonnet-4-6)
        → merge all raw data → structured KPI JSON
        → icp_score, intent_score, engagement_readiness, campaign_type_match
        → personalization_tags, competitive_intel, pain_point_clusters
        Cost: ~$0.002/lead

Step 5: Embedding Generation (text-embedding-3-small or Claude Embeddings)
        → 1536-dim vector stored in pgvector
        → used for: duplicate detection + segment clustering
        Cost: ~$0.0001/lead
```

**Parallelism:** Steps 1, 2, and 3 run concurrently (`asyncio.gather`). Step 4 runs after all three complete. Step 5 runs after Step 4.

**Retry policy:** Steps 1–3: max 2 retries with exponential backoff. Steps 4–5: max 3 retries. Failed leads get `status = 'research_failed'` with error stored in `research_log`.

**Cost estimate per 1,000 leads:** ~$3–8 USD depending on research depth.

---

## 8. Duplicate Detection Logic

### Phase 1 — Exact Match (runs at upload time, synchronous)
```
Hash: MD5(email.lower().strip())
Hash: MD5(phone digits only)
If either hash exists in leads table → flag as duplicate, set duplicate_of
```

### Phase 2 — Fuzzy Match (runs as background task after Phase 1)
```
Input string: "{name} {company_name} {job_title}"
Generate embedding → cosine similarity search via pgvector (top 5 neighbours)
Similarity threshold: > 0.92 → flag as likely duplicate for human review
Similarity threshold: > 0.97 → auto-merge (copy best fields, archive duplicate)
```

### Merge Rules (when merging two leads)
- Keep the lead with more non-null enrichment fields
- Prefer `email_verified = True` over unverified
- Union `personalization_tags[]` and `pain_point_clusters[]`
- Keep higher scores (`icp_score`, `intent_score`)
- Preserve both `raw_csv_data` entries in the winning lead's JSONB array
- Log the merge in `research_log` with `source = 'deduplicator'`

---

## 9. API Routes

All routes prefixed `/api/v1/`. All responses use Pydantic schemas. All list routes support `limit` + `offset` pagination.

### Upload
| Method | Route | Description |
|---|---|---|
| `POST` | `/upload/csv` | Upload CSV file, parse, validate, queue dedup + research |
| `GET` | `/upload/jobs` | List recent upload jobs with status + progress |
| `GET` | `/upload/jobs/{job_id}` | Single job status (total / processed / failed / duplicates_found) |

### Leads
| Method | Route | Description |
|---|---|---|
| `GET` | `/leads` | List leads with filters (status, icp_score, industry, region, etc.) |
| `POST` | `/leads` | Create lead manually; auto-creates Company record if `company_name` given |
| `GET` | `/leads/{id}` | Full lead detail with all KPIs + research log |
| `PATCH` | `/leads/{id}` | Manual field update (override AI-classified values) |
| `DELETE` | `/leads/{id}` | Soft delete (status = invalid) |
| `DELETE` | `/leads` | Hard delete **all** leads (returns `{"deleted": N}`); use with care |
| `POST` | `/leads/{id}/research` | Enqueue research task; stores ARQ job ID on lead |
| `POST` | `/leads/{id}/cancel-research` | Abort ARQ job (best-effort) + reset status to `raw` |
| `GET` | `/leads/export` | Export filtered leads as CSV |

### Companies
| Method | Route | Description |
|---|---|---|
| `GET` | `/companies` | List companies with filters |
| `GET` | `/companies/{id}` | Company detail + all associated leads |
| `PATCH` | `/companies/{id}` | Manual update |
| `POST` | `/companies/{id}/research` | Trigger re-research for company |

### Duplicates
| Method | Route | Description |
|---|---|---|
| `GET` | `/duplicates` | List pending duplicate review pairs |
| `POST` | `/duplicates/{id}/merge` | Confirm merge (keep lead A, archive B) |
| `POST` | `/duplicates/{id}/dismiss` | Mark as not a duplicate |

### Segments
| Method | Route | Description |
|---|---|---|
| `GET` | `/segments` | List all segments with lead counts |
| `POST` | `/segments` | Create new segment (name + filter_rules JSON) |
| `GET` | `/segments/{id}` | Segment detail + matching lead preview (first 20) |
| `GET` | `/segments/{id}/leads` | Paginated leads matching this segment |
| `PUT` | `/segments/{id}` | Update filter rules |
| `DELETE` | `/segments/{id}` | Delete segment |
| `POST` | `/segments/{id}/export` | Export segment leads as CSV |
| `POST` | `/segments/preview` | Preview lead count for a filter_rules JSON (before saving) |

### KPI & Analytics
| Method | Route | Description |
|---|---|---|
| `GET` | `/analytics/overview` | High-level stats: total leads, enriched %, avg ICP score, etc. |
| `GET` | `/analytics/by-industry` | Lead count + avg scores grouped by industry |
| `GET` | `/analytics/by-region` | Lead count + avg scores grouped by region |
| `GET` | `/analytics/by-funding-stage` | Lead count grouped by funding stage |
| `GET` | `/analytics/by-company-size` | Lead count grouped by company size |
| `GET` | `/analytics/icp-distribution` | Histogram of ICP scores |
| `GET` | `/analytics/research-cost` | Cost breakdown by source + date range |

### Research
| Method | Route | Description |
|---|---|---|
| `GET` | `/research/logs` | Paginated research log with filters (lead_id, source, success); includes `duration_ms` |
| `GET` | `/research/queue` | All leads with `status=researching`; includes `paused` boolean flag |
| `POST` | `/research/cancel-all` | Abort all queued ARQ jobs; reset all researching leads to `raw` |
| `POST` | `/research/pause` | Set `RESEARCH_PAUSED=true` in app_settings; worker checks this fresh per task |
| `POST` | `/research/resume` | Clear `RESEARCH_PAUSED`; re-enqueue all leads still in `researching` state |
| `POST` | `/research/retry-failed` | Re-queue leads with `status=research_failed` or `raw` |

### Admin
| Method | Route | Description |
|---|---|---|
| `GET` | `/admin/settings` | List all settings with current value, source (db/env/unset), and masked display for secrets |
| `PUT` | `/admin/settings/{key}` | Upsert a setting; sanitizes invisible Unicode from value; updates in-memory cache |
| `DELETE` | `/admin/settings/{key}` | Remove DB override (env var fallback takes effect again) |
| `GET` | `/admin/logs` | Recent in-memory app logs (max 500 entries); excluded from request log middleware to prevent recursion |

### Campaigns (stub — schema only until Phase 9)
| Method | Route | Description |
|---|---|---|
| `GET` | `/campaigns` | List campaigns |
| `POST` | `/campaigns` | Create campaign from segment |

---

## 10. Frontend Pages

```
[ Upload ] [ Leads ] [ Companies ] [ Duplicates ] [ Research ] [ Segments ] [ KPI Dashboard ] [ Campaigns* ]
                                                                                               *stub until Phase 9
```

### Upload Page
- Drag-and-drop CSV upload zone
- CSV column mapper (auto-detect → manual override if needed)
- Upload job progress tracker (WebSocket or polling)
- Validation errors list (missing required fields, malformed emails)

### Leads Page
- Filterable data table: all KPI fields as filter options
- **Column picker** — toggle any of the 20 Lead model fields on/off; persisted to `localStorage`
- **Checkbox multi-select** — "Delete N selected" with confirmation modal
- Inline score badges (ICP / Intent / Engagement) with colour coding
- Lead detail slide-in drawer: all KPIs, research log, raw CSV row
- Bulk actions: trigger research, export, add to segment, delete all, delete selected
- Add Lead modal: manual entry of name/email/phone/title/company/LinkedIn
- Status badges: raw / researching / enriched / duplicate / merged / invalid

### Companies Page
- Company cards with key metrics
- Click → company detail: all KPIs + associated leads list
- Research status indicator per company

### Duplicates Page
- Side-by-side comparison of duplicate lead pairs
- Field-level diff highlighting
- One-click merge or dismiss
- Confidence score shown per pair

### Research Page
- **QueuePanel** — amber banner at top; auto-polls every 2.5 s; shows all leads currently in `researching` state; turns grey when paused; hides when queue is empty and not paused
  - Per-lead cancel (✕) button
  - "Pause All / Resume" toggle — sets `RESEARCH_PAUSED` flag via API
  - "Cancel All" button — resets all queued leads to `raw`
- Per-lead research log table: source, tokens, cost, **duration**, full datetime
- Source filter includes: serper / playwright / hunter / claude / gemini / openai / ai
- Retry failed leads button
- Expand row to see raw API response and error message

### Segments Page
- Segment list with live lead counts
- Visual filter builder (add rules, see matching count update in real-time)
- Save as named segment
- Export or push to campaign

### KPI Dashboard
```
Row 1: Total Leads | Enriched % | Avg ICP Score | Decision Makers % | Email Verified %

Row 2: [Industry breakdown bar chart] [Region breakdown bar chart]

Row 3: [Funding Stage pie] [Company Size pie] [ICP Score histogram]

Row 4: [Intent Score distribution] [Engagement Readiness distribution]

Row 5: [Research cost by source] [Research pipeline status]
```

All charts use `recharts`. All KPI labels carry `data-tip` for tooltip onboarding.

---

## 11. Research APIs — Paid vs Free

| API | Purpose | Free Tier | Cost at Scale |
|---|---|---|---|
| **Serper** | Google search (company news, funding, people) | 2,500 queries free | $50/mo → 50k queries |
| **Hunter.io** | Email verification by domain | 25 searches/mo | $49/mo → 500 |
| **Playwright** | Website scraping (self-hosted) | Free | Your compute only |
| **Claude API** | Synthesize research → KPI JSON | Pay per token | ~$0.002/lead |
| **Tavily** *(optional)* | AI-optimised web research (alternative to Serper) | 1,000 queries/mo | $20/mo → 10k |
| **Snov.io** *(optional)* | Email finder + verify (alternative to Hunter) | 50 credits/mo | $39/mo |
| **Apollo.io** *(optional)* | Full contact enrichment (email + title + company) | 50 credits/mo | $49/mo → 10k |

**Phase 1 recommendation (local, cost-controlled):**
Use Serper + Hunter.io free tiers + Playwright + Claude. This covers 2,500 leads/mo at near-zero cost.

All API keys stored in `.env` and loaded via `config.py`. Never hardcoded.

---

## 12. Hard Rules (breaking these causes bad data or cost overruns)

1. **Never call research APIs from a route handler.** Always queue as an ARQ task. Routes are for fast CRUD only.
2. **Never run duplicate detection on un-normalised email.** Always `email.lower().strip()` before hashing or comparing.
3. **Never store API keys in source code.** Every secret goes in `.env`, loaded by `pydantic-settings`.
4. **Always log to `research_log` before storing enriched data.** This is the audit trail; without it, cost tracking breaks.
5. **pgvector index must exist before inserting embeddings.** `CREATE INDEX USING ivfflat` in Alembic migration — not in application code.
6. **Alembic only for schema changes.** Never `ALTER TABLE` manually or via SQLAlchemy `create_all()` in production.
7. **All CSV columns must map to known schema fields.** Unknown columns go into `lead.raw_csv_data` as JSONB — never dropped silently.
8. **Email campaigns (Phase 9) cannot send to unverified emails.** `email_deliverability = 'deliverable'` is a hard gate before any send.
9. **ARQ tasks must be idempotent.** If a task is retried, it must not create duplicate research_log entries or overwrite better data with worse.
10. **No direct DB access in frontend.** React communicates only via the FastAPI REST layer.

---

## 13. Environment Variables

All defined in `other_items_to_install/.env.example`. Required before any service starts.

```
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/marketing_db

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=<random 64-char hex>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# AI
CLAUDE_API_KEY=
CLAUDE_MODEL=claude-sonnet-4-6

# Research APIs
SERPER_API_KEY=
HUNTER_API_KEY=
TAVILY_API_KEY=           # optional, alternative to Serper
APOLLO_API_KEY=           # optional, for contact enrichment

# Optional AI providers
OPENAI_API_KEY=
GEMINI_API_KEY=

# Feature flags
RESEARCH_ENABLED=true
DEDUP_AUTO_MERGE_THRESHOLD=0.97
DEDUP_REVIEW_THRESHOLD=0.92
MAX_CONCURRENT_RESEARCH_WORKERS=4
```

---

## 14. Design System

Every agent adding UI must follow this system. It exists so the app feels like one product, not accumulated patches.

### Color Tokens (Tailwind CSS custom palette)

| Token | Hex | Use |
|---|---|---|
| `brand-900` | `#0d1b4b` | Primary navy — headers, active nav |
| `brand-700` | `#1a2f7a` | Lighter navy — hover, buttons |
| `brand-500` | `#3b5bdb` | Interactive blue — links, badges |
| `success-700` | `#1b7a3b` | Hot / BUY / positive / verified |
| `success-100` | `#dcfce7` | Success background |
| `danger-700` | `#c0392b` | Cold / negative / unverified |
| `danger-100` | `#fee2e2` | Danger background |
| `warning-500` | `#f39c12` | Pending / in-progress |
| `warning-100` | `#fef9e7` | Warning background |
| `neutral-500` | `#6c757d` | Muted text, secondary labels |
| `border` | `#e2e6ef` | Card borders, dividers |
| `page-bg` | `#f1f5f9` | Page background |

**Semantic rules:**
- Green: always positive / verified / hot / enriched
- Red: always negative / failed / cold / invalid
- Blue: interactive / neutral information
- Amber: pending / in-progress / requires attention
- Never mix semantic meanings across contexts

### ICP Score Colour Coding (consistent across all pages)

| Range | Label | Colour |
|---|---|---|
| 70–100 | Hot | Green (`success-700`) |
| 40–69 | Warm | Amber (`warning-500`) |
| 0–39 | Cold | Red (`danger-700`) |

Same banding for Intent Score and Engagement Readiness.

### Typography Scale

| Size | Weight | Use |
|---|---|---|
| `text-xs` (12px) | 400 | Metadata, timestamps, badges |
| `text-sm` (14px) | 400 / 500 | Table cells, secondary body |
| `text-base` (16px) | 400 | Primary body text |
| `text-lg` (18px) | 600 | Card titles, sub-headings |
| `text-xl` (20px) | 700 | Page section headings |
| `text-2xl` (24px) | 700 | KPI stat values |
| `text-3xl` (30px) | 800 | Dashboard hero numbers |

### Spacing System

Use Tailwind spacing only: `p-1 p-2 p-3 p-4 p-5 p-6 p-8 p-10 p-12`. No arbitrary values like `p-[15px]`. Card inner padding: `p-4` or `p-5`. Modal padding: `p-6`.

### Component Patterns

**Status badges** — pill shape, consistent colours:
```
raw          → grey bg   + grey text    ("Raw")
researching  → blue bg   + blue text    ("Researching...")
enriched     → green bg  + green text   ("Enriched")
duplicate    → amber bg  + amber text   ("Duplicate")
merged       → purple bg + purple text  ("Merged")
invalid      → red bg    + red text     ("Invalid")
```

**Score chips** — circular number badge:
- Use `bg-success-100 text-success-700` for Hot (>70)
- Use `bg-warning-100 text-warning-500` for Warm (40–70)
- Use `bg-danger-100 text-danger-700` for Cold (<40)

**Charts** — `recharts` only. Use `ResponsiveContainer` wrapper. Consistent palette:
- Series 1: `#3b5bdb`
- Series 2: `#1b7a3b`
- Series 3: `#f39c12`
- Series 4: `#c0392b`
- Grid lines: `#e2e6ef`
- Axis text: `#6c757d`

**Transitions:** All hover states: `transition-all duration-150 ease-in-out`. Drawer/modal entry: `transition-transform duration-200 ease-out`.

---

## 15. Roadmap

| Phase | Status | Description | Exit Gate |
|---|---|---|---|
| 1 — Infrastructure | planned | Docker, Postgres+pgvector, Redis, FastAPI + React skeletons, Alembic | All 5 services start; migrations apply cleanly |
| 2 — Ingestion | planned | CSV upload, parse, validate, store raw leads | Upload 1,000 leads from CSV, all stored in DB |
| 3 — Deduplication | planned | Exact match + pgvector semantic dedup + merge UI | Dedup correctly on a test CSV with known duplicates |
| 4 — Research Pipeline | planned | Playwright + Serper + Hunter + Claude synthesis, ARQ workers | 10 leads fully enriched with all KPI fields |
| 5 — AI Classification | planned | Industry, region, business type, ICP/Intent/Engagement scores | Classifications validated against manual ground truth |
| 6 — Segmentation | planned | Rule-based filter builder + AI cluster suggestions | Named segment created; export to CSV works |
| 7 — KPI Dashboard | planned | All chart breakdowns, filter controls | Dashboard renders with 100+ enriched leads |
| 8 — Campaign Prep | planned | Segment review, personalisation tag audit, email template builder | Template renders with correct variable substitution |
| 9 — Email Automation | planned | Sending engine, tracking, unsubscribe, campaign analytics | End-to-end campaign sent to 10 test leads |

---

## 16. Tech Debt Tracker

| Item | Priority | Notes |
|---|---|---|
| Playwright browser pool | Medium | Single browser per worker is slow; add shared pool when research volume > 500/day |
| Embedding model choice | Low | Defaulting to `text-embedding-3-small`; upgrade to `text-embedding-3-large` if clustering quality is poor |
| CSV column auto-mapping | Medium | Implement fuzzy header matching (e.g. "Email Address" → `email`) before Phase 2 ships |
| Rate limiting | High | Add per-user request rate limiting on upload + research endpoints before any external exposure |

---

## 17. Knowledge Graph (graphify)

**graphify is permanently installed. Never run `pip install` — skip that step entirely.**

```
Python  : /opt/homebrew/opt/python@3.13/bin/python3.13
Output  : marketing_project/graphify-out/
```

### Current graph state (2026-05-28)

| Metric | Value |
|---|---|
| Nodes | 466 |
| Edges | 692 |
| Communities | 33 |
| Edge breakdown | 85% EXTRACTED · 15% INFERRED |
| Source files | 82 (79 code, 3 docs) |

Output files:
| File | Purpose |
|---|---|
| `graphify-out/graph.json` | GraphRAG-ready node/edge data with community assignments |
| `graphify-out/graph.html` | Interactive HTML visualization — open in browser |
| `graphify-out/GRAPH_REPORT.md` | Plain-language report: god nodes, communities, surprises, suggested questions |
| `graphify-out/cache/` | Per-file extraction cache — speeds up incremental runs |

### How to run graphify

**Full rebuild** (run after major restructuring):
```bash
cd /Users/himanshumittal/Extra/Odoo/client/theerpbot/dev/marketing_project
# In Claude Code, type:
/graphify .
```

**Incremental update** (run after adding/changing files — uses cache, only re-extracts changed files):
```bash
cd /Users/himanshumittal/Extra/Odoo/client/theerpbot/dev/marketing_project
/graphify . --update
```

**View the graph** — open in browser:
```bash
open /Users/himanshumittal/Extra/Odoo/client/theerpbot/dev/marketing_project/graphify-out/graph.html
```

**Query the graph** (ask a question about the codebase):
```bash
# In Claude Code:
/graphify query "How does a lead flow from CSV upload through research to enrichment?"
/graphify query "Which services depend on ai_client.py?"
/graphify explain "research_lead"
```

### When to update the graph

Run `/graphify . --update` after:
- Adding a new service, router, or model
- Adding a new ARQ worker task
- Adding a new frontend page or major component
- Completing a new Phase (as defined in §15)

The incremental `--update` flag only re-extracts files that changed since the last run. On a warm cache, it completes in under 10 seconds.

### God nodes (most connected — core abstractions as of last run)

1. `marketing_project` — 21 edges (project root / top-level concept)
2. `FastAPI REST API Service` — 20 edges (API layer hub)
3. `Lead` — 19 edges (central data model, bridges upload ↔ research ↔ dedup ↔ classify)
4. `PaginatedResponse` — 14 edges (shared response schema)
5. `User` — 12 edges (auth + ownership)
6. `Base` — 11 edges (SQLAlchemy declarative base)
7. `React Frontend Service` — 11 edges (frontend layer hub)
8. `upload_file()` — 10 edges (ingestion entry point)
9. `research_lead()` — 8 edges (pipeline orchestrator — bridges DB, search, AI, email verify)

These are the nodes to study first when onboarding. Touching any of them has broad downstream effects.

---

## 18. Versioning Policy

### Format: `MAJOR.MINOR.PATCH`

Stored in one place only: `marketing_app/backend/app/version.py`

```python
# marketing_app/backend/app/version.py
__version__ = "0.1.0"
```

Exposed automatically at `GET /api/v1/version` (no auth required). The frontend reads it on load and displays it in the footer.

---

### When to bump what

| Change type | Bump | Example |
|---|---|---|
| Breaking API change — route removed, response shape changed, field renamed | **MAJOR** | `0.9.0 → 1.0.0` |
| New DB migration (table/column added) | **MINOR** | `0.1.0 → 0.2.0` |
| New route or new page added | **MINOR** | `0.2.0 → 0.3.0` |
| New worker task or research source added | **MINOR** | `0.3.0 → 0.4.0` |
| New KPI field on leads or companies | **MINOR** | `0.4.0 → 0.5.0` |
| Bug fix — no schema/API change | **PATCH** | `0.5.0 → 0.5.1` |
| UI/UX fix — no backend change | **PATCH** | `0.5.1 → 0.5.2` |
| Dependency update, config change, refactor | **PATCH** | `0.5.2 → 0.5.3` |
| AGENTS.md update only | **no bump** | — |

**Rule: one PR = one version bump.** Never batch multiple MINOR changes under one version silently. If a PR adds two new routes and a migration, that is still one MINOR bump — describe all changes in the Feature Log entry.

**Rule: MAJOR bumps require explicit confirmation from the project owner.** Do not bump MAJOR unilaterally.

---

### Feature Log format (what each row must contain)

```
| {version} | {YYYY-MM-DD} | {short title} | {done|in_progress|planned} | {description} |
```

Description must state: **what** was built, **why** (the problem it solves or the phase it unlocks), and any **hard decisions** made (e.g. "chose Serper over Tavily because cost per query is 5× lower at volume"). One paragraph max.

---

### Version lifecycle per phase

| Phase | Version range | Notes |
|---|---|---|
| Phase 1 — Infrastructure | `0.1.x` | Scaffold only, no business logic |
| Phase 2 — Ingestion | `0.2.x` | CSV upload + raw lead storage |
| Phase 3 — Deduplication | `0.3.x` | Exact + fuzzy dedup + merge UI |
| Phase 4 — Research Pipeline | `0.4.x` | ARQ workers, all research sources |
| Phase 5 — AI Classification | `0.5.x` | KPI scoring + classification |
| Phase 6 — Segmentation | `0.6.x` | Filter builder + clusters |
| Phase 7 — KPI Dashboard | `0.7.x` | Charts + analytics routes |
| Phase 8 — Campaign Prep | `0.8.x` | Templates + personalisation |
| Phase 9 — Email Automation | `1.0.0` | First production-ready major |

Minor versions within a phase (e.g. `0.4.3`) are patch-level fixes inside that phase. A phase is never "done" at exactly `x.0` — real work always produces patches.

---

### Alembic migration naming convention

Every migration file must include the version it belongs to:

```
migrations/versions/{YYYYMMDD}_{version}_{short_description}.py

Examples:
  20260527_0.1.0_initial_schema.py
  20260528_0.2.0_add_leads_table.py
  20260530_0.3.1_add_embedding_index.py
```

This makes it immediately clear which feature introduced which schema change, without digging through git log.

---

### Git commit convention

```
{type}({scope}): {description}  [v{version}]

Types : feat | fix | refactor | docs | chore | test
Scope : backend | frontend | worker | db | docker | agents

Examples:
  feat(backend): add CSV upload endpoint [v0.2.0]
  fix(worker): retry on Playwright timeout [v0.2.1]
  feat(db): add pgvector embedding index [v0.3.0]
  docs(agents): update KPI taxonomy [no version bump]
```

The `[v{version}]` tag at the end makes `git log --oneline` readable as a changelog without any extra tooling.
