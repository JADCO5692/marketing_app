"""
Email verification via Hunter.io.
Checks deliverability status before any campaign send.
"""
import httpx
from app.config import settings


async def verify_email(email: str) -> dict:
    """
    Verify an email address via Hunter.io.
    Returns dict with: status, score, type, mx_found, smtp_check, disposable.
    Returns {} on failure or missing API key.
    """
    if not settings.HUNTER_API_KEY or not email:
        return {}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://api.hunter.io/v2/email-verifier",
                params={"email": email, "api_key": settings.HUNTER_API_KEY},
            )
            response.raise_for_status()
            data = response.json().get("data", {})

        return {
            "status": data.get("status"),           # deliverable / risky / undeliverable
            "score": data.get("score"),              # 0–100 confidence
            "email_type": data.get("type"),          # personal / generic / role-based
            "mx_found": data.get("mx_found"),
            "smtp_check": data.get("smtp_check"),
            "disposable": data.get("disposable"),
        }
    except Exception:
        return {}


async def find_emails_by_domain(domain: str, limit: int = 5) -> list[dict]:
    """Find email addresses associated with a domain via Hunter."""
    if not settings.HUNTER_API_KEY or not domain:
        return []

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://api.hunter.io/v2/domain-search",
                params={"domain": domain, "limit": limit, "api_key": settings.HUNTER_API_KEY},
            )
            response.raise_for_status()
            data = response.json().get("data", {})

        return [
            {
                "email": e.get("value"),
                "type": e.get("type"),
                "first_name": e.get("first_name"),
                "last_name": e.get("last_name"),
                "position": e.get("position"),
                "confidence": e.get("confidence"),
            }
            for e in data.get("emails", [])
        ]
    except Exception:
        return []
