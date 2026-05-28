"""
Single gateway for all AI calls.

Provider selection (in priority order):
  1. Claude  — if CLAUDE_API_KEY is set
  2. Gemini  — if GEMINI_API_KEY is set
  3. OpenAI  — if OPENAI_API_KEY is set

The active key is read from the settings service on every call so DB
overrides take effect without a restart.
"""
import json
from app.services.settings_service import get_setting

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


def _active_provider() -> str:
    if get_setting("CLAUDE_API_KEY"):
        return "claude"
    if get_setting("GEMINI_API_KEY"):
        return "gemini"
    if get_setting("OPENAI_API_KEY"):
        return "openai"
    raise ValueError(
        "No AI provider configured. "
        "Set CLAUDE_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY in Settings."
    )


async def chat(
    system: str,
    user: str,
    model: str | None = None,
    max_tokens: int = 2000,
    temperature: float = 0.2,
) -> str:
    """Send a chat request to the active AI provider."""
    provider = _active_provider()

    if provider == "claude":
        import anthropic
        client = anthropic.AsyncAnthropic(
            api_key=get_setting("CLAUDE_API_KEY")
        )
        response = await client.messages.create(
            model=model or get_setting("CLAUDE_MODEL") or "claude-sonnet-4-6",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text

    if provider == "gemini":
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=get_setting("GEMINI_API_KEY"))
        response = await client.aio.models.generate_content(
            model=model or DEFAULT_GEMINI_MODEL,
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )
        return response.text

    if provider == "openai":
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=get_setting("OPENAI_API_KEY"))
        response = await client.chat.completions.create(
            model=model or "gpt-4o-mini",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content


async def chat_json(system: str, user: str, **kwargs) -> dict:
    """Like chat() but parses the response as JSON."""
    raw = await chat(system, user, **kwargs)
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return json.loads(text)
