from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class UploadJobResponse(BaseModel):
    job_id: str
    filename: str
    status: str          # queued/processing/done/failed
    total_rows: int
    processed: int
    stored: int
    duplicates_found: int
    failed_rows: int
    errors: list[str]
    created_at: datetime


class CsvColumnMapping(BaseModel):
    """Map CSV header names to lead fields. Unknown columns go to raw_csv_data."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    company_name: Optional[str] = None
    company_domain: Optional[str] = None
