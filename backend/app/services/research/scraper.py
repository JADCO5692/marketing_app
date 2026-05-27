"""
Website scraper using Playwright.
Extracts: company description, product/service text, contact page signals, tech stack hints.
"""
from __future__ import annotations


async def scrape_website(domain: str) -> dict:
    """
    Scrape a company website and return structured data.
    Returns empty dict on any failure — callers must handle gracefully.
    """
    if not domain:
        return {}

    url = domain if domain.startswith("http") else f"https://{domain}"

    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (compatible; MarketingBot/1.0)"
            )
            page = await context.new_page()
            await page.goto(url, timeout=15000, wait_until="domcontentloaded")

            title = await page.title()
            meta_desc = await page.get_attribute('meta[name="description"]', "content") or ""
            body_text = await page.inner_text("body")
            # Trim to 3000 chars to stay within AI token budget
            body_text = body_text[:3000].strip()

            await browser.close()

        return {
            "url": url,
            "title": title,
            "meta_description": meta_desc,
            "body_excerpt": body_text,
        }

    except Exception as exc:
        return {"url": url, "error": str(exc)[:200]}
