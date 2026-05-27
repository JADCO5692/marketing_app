"""
Generate 1536-dim embeddings for leads.
Used by: duplicate detection (pgvector cosine similarity) and segment clustering.
"""
from app.config import settings


def _lead_text(lead_data: dict) -> str:
    parts = [
        lead_data.get("name") or "",
        lead_data.get("job_title") or "",
        lead_data.get("company_name") or "",
        lead_data.get("department") or "",
    ]
    return " ".join(p for p in parts if p).strip()


async def embed_text(text: str) -> list[float] | None:
    """Generate a 1536-dim embedding via OpenAI text-embedding-3-small."""
    if not text.strip():
        return None
    try:
        import openai
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding
    except Exception:
        return None


async def embed_lead(lead_data: dict) -> list[float] | None:
    text = _lead_text(lead_data)
    return await embed_text(text) if text else None
