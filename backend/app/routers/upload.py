import csv
import hashlib
import io
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.lead import Lead
from app.models.company import Company
from app.schemas.upload import UploadJobResponse
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter()

# In-memory job store — sufficient for Phase 1 single-server local use.
# Replace with Redis-backed store when horizontal scaling is needed.
_jobs: dict[str, dict] = {}

KNOWN_FIELDS = {"name", "email", "phone", "linkedin_url", "job_title", "department"}
COMPANY_FIELDS = {"company_name", "company_domain", "company", "domain"}


def _normalize_header(h: str) -> str:
    return h.strip().lower().replace(" ", "_")


def _email_hash(email: str) -> str:
    return hashlib.md5(email.lower().strip().encode()).hexdigest()


def _phone_digits(phone: str) -> str:
    return "".join(c for c in phone if c.isdigit())


@router.post("/csv", response_model=UploadJobResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    content = await file.read()
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    job: dict = {
        "job_id": job_id,
        "filename": file.filename,
        "status": "processing",
        "total_rows": 0,
        "processed": 0,
        "stored": 0,
        "duplicates_found": 0,
        "failed_rows": 0,
        "errors": [],
        "created_at": now,
    }
    _jobs[job_id] = job

    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
    rows = list(reader)
    job["total_rows"] = len(rows)

    # Load all existing email hashes and phone digests for fast exact dedup
    existing_emails_result = await db.execute(select(Lead.email).where(Lead.email.isnot(None)))
    existing_emails = {_email_hash(r) for r in existing_emails_result.scalars().all()}
    existing_phones_result = await db.execute(select(Lead.phone).where(Lead.phone.isnot(None)))
    existing_phones = {_phone_digits(r) for r in existing_phones_result.scalars().all() if r}

    leads_to_add: list[Lead] = []

    for row_num, row in enumerate(rows, start=2):
        job["processed"] += 1
        try:
            normalized = {_normalize_header(k): v.strip() if v else "" for k, v in row.items() if k}

            email = normalized.get("email") or None
            phone = normalized.get("phone") or None

            # Exact duplicate check
            if email and _email_hash(email) in existing_emails:
                job["duplicates_found"] += 1
                continue
            if phone and _phone_digits(phone) and _phone_digits(phone) in existing_phones:
                job["duplicates_found"] += 1
                continue

            # Build lead
            lead_fields = {k: normalized.get(k) or None for k in KNOWN_FIELDS}
            raw = {k: v for k, v in normalized.items() if k not in KNOWN_FIELDS and k not in COMPANY_FIELDS and v}

            lead = Lead(
                **{k: v for k, v in lead_fields.items() if v},
                raw_csv_data=raw if raw else None,
                source_file=file.filename,
                source_row=row_num,
                status="raw",
            )
            leads_to_add.append(lead)

            if email:
                existing_emails.add(_email_hash(email))
            if phone and _phone_digits(phone):
                existing_phones.add(_phone_digits(phone))

        except Exception as exc:
            job["failed_rows"] += 1
            job["errors"].append(f"Row {row_num}: {exc}")

    db.add_all(leads_to_add)
    await db.commit()

    job["stored"] = len(leads_to_add)
    job["status"] = "done"
    return UploadJobResponse(**job)


@router.get("/jobs", response_model=list[UploadJobResponse])
async def list_jobs(current_user: User = Depends(get_current_user)):
    return [UploadJobResponse(**j) for j in sorted(_jobs.values(), key=lambda x: x["created_at"], reverse=True)]


@router.get("/jobs/{job_id}", response_model=UploadJobResponse)
async def get_job(job_id: str, current_user: User = Depends(get_current_user)):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return UploadJobResponse(**job)
