"""
Single gateway for all AI calls. Never call anthropic/openai directly from a route or worker.
All calls go through this module so provider can be swapped without touching business logic.
"""
import json
from app.config import settings


async def chat(
    system: str,
    user: str,
    model: str | None = None,
    max_tokens: int = 2000,
    temperature: float = 0.2,
) -> str:
    """Send a chat request to the configured AI provider. Returns the text response."""
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)
    response = await client.messages.create(
        model=model or settings.CLAUDE_MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text


async def chat_json(system: str, user: str, **kwargs) -> dict:
    """Like chat() but parses the response as JSON. Raises ValueError on parse failure."""
    raw = await chat(system, user, **kwargs)
    # Strip markdown code fences if the model wraps with them
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return json.loads(text)
