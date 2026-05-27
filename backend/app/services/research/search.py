"""
Google search via Serper API.
Used for: company news, funding announcements, job postings, key people.
"""
import httpx
from app.config import settings


async def search(query: str, num_results: int = 5) -> list[dict]:
    """
    Run a Google search via Serper and return result snippets.
    Returns [] on failure or missing API key.
    """
    if not settings.SERPER_API_KEY:
        return []

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": settings.SERPER_API_KEY, "Content-Type": "application/json"},
                json={"q": query, "num": num_results},
            )
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("organic", [])[:num_results]:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "link": item.get("link", ""),
            })
        return results

    except Exception:
        return []


async def research_company(company_name: str, domain: str | None = None) -> dict:
    """Run multiple targeted searches for a company and aggregate results."""
    queries = [
        f"{company_name} company overview funding",
        f"{company_name} news 2024 2025",
        f"{company_name} {domain or ''} hiring jobs".strip(),
    ]
    all_results = []
    for q in queries:
        all_results.extend(await search(q, num_results=3))

    return {"query_count": len(queries), "results": all_results}
