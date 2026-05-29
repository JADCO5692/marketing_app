"""
AI synthesis step — merges all raw research sources into structured KPI JSON.
This is the final step in the research pipeline, after scrape + search + email verify.
The system prompt is loaded from the RESEARCH_PROMPT_TEMPLATE setting at call time so
it can be customised via the Settings UI without redeploying.
"""
import logging
from app.services.ai_client import chat_json
from app.services.settings_service import get_setting, _DEFAULT_RESEARCH_PROMPT

logger = logging.getLogger("app.synthesizer")


async def synthesize(
    lead_raw: dict,
    company_raw: dict,
    website_data: dict,
    search_results: list[dict],
    email_verification: dict,
) -> dict | None:
    """
    Synthesize all research into structured KPI fields.
    Returns None on failure so the worker can log and continue.
    System prompt is read from the RESEARCH_PROMPT_TEMPLATE setting at call time
    so UI changes take effect without a restart.
    """
    system = get_setting("RESEARCH_PROMPT_TEMPLATE", default=_DEFAULT_RESEARCH_PROMPT)
    prompt = f"""
Contact raw data:
{lead_raw}

Company raw data:
{company_raw}

Website scrape:
{website_data}

Search results:
{search_results[:5]}

Email verification:
{email_verification}

Synthesize all of this into the structured JSON format.
"""
    try:
        return await chat_json(system, prompt, max_tokens=1500)
    except Exception as exc:
        logger.error("Synthesis failed: %s", exc)
        return None
