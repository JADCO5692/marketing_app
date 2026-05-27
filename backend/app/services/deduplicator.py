"""
Duplicate detection — two phases:
  Phase 1 (synchronous, at upload): exact hash match on email + phone.
  Phase 2 (async worker): pgvector cosine similarity on name+company embedding.
"""
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.config import settings
from app.models.lead import Lead
import uuid


def email_hash(email: str) -> str:
    return hashlib.md5(email.lower().strip().encode()).hexdigest()


def phone_digits(phone: str) -> str:
    return "".join(c for c in phone if c.isdigit())


async def find_semantic_duplicates(
    db: AsyncSession,
    lead_id: uuid.UUID,
    embedding: list[float],
    threshold: float | None = None,
) -> list[tuple[uuid.UUID, float]]:
    """
    Query pgvector for leads with cosine similarity above threshold.
    Returns list of (lead_id, similarity) pairs, excluding the lead itself.
    Phase 3 activates this; returns [] until embeddings are populated.
    """
    if not embedding:
        return []

    auto_threshold = threshold or settings.DEDUP_REVIEW_THRESHOLD
    vec_str = "[" + ",".join(str(v) for v in embedding) + "]"

    result = await db.execute(
        text("""
            SELECT id, 1 - (embedding <=> :vec::vector) AS similarity
            FROM leads
            WHERE id != :lead_id
              AND embedding IS NOT NULL
              AND status NOT IN ('invalid', 'merged')
              AND 1 - (embedding <=> :vec::vector) >= :threshold
            ORDER BY similarity DESC
            LIMIT 10
        """),
        {"vec": vec_str, "lead_id": str(lead_id), "threshold": auto_threshold},
    )
    return [(uuid.UUID(str(row[0])), float(row[1])) for row in result.fetchall()]


async def process_semantic_dedup(db: AsyncSession, lead: Lead) -> int:
    """
    Run semantic dedup for a single lead. Returns number of duplicates flagged.
    Called from the ARQ worker after embedding generation.
    """
    if not lead.embedding:
        return 0

    matches = await find_semantic_duplicates(db, lead.id, lead.embedding)
    flagged = 0

    for match_id, similarity in matches:
        match = await db.get(Lead, match_id)
        if not match or match.status in ("invalid", "merged", "duplicate"):
            continue

        if similarity >= settings.DEDUP_AUTO_MERGE_THRESHOLD:
            # Auto-merge: keep the older lead (lower created_at), archive the newer
            if lead.created_at <= match.created_at:
                match.status = "duplicate"
                match.duplicate_of = lead.id
            else:
                lead.status = "duplicate"
                lead.duplicate_of = match.id
        else:
            # Flag for human review
            if lead.status != "duplicate":
                lead.status = "duplicate"
                lead.duplicate_of = match.id
        flagged += 1

    return flagged
