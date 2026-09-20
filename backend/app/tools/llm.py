import json
from app.core.config import settings

_client = None


def _get_client():
    global _client
    if _client is None and settings.anthropic_api_key:
        from anthropic import Anthropic
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


def is_live() -> bool:
    return bool(settings.anthropic_api_key)


def call_json(system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> dict:
    client = _get_client()
    if not client:
        raise RuntimeError("No Anthropic API key configured, caller should use fallback path")

    response = client.messages.create(
        model=settings.llm_model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text_blocks = [block.text for block in response.content if block.type == "text"]
    raw_text = "".join(text_blocks).strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    return json.loads(raw_text)


def call_text(system_prompt: str, user_prompt: str, max_tokens: int = 800) -> str:
    client = _get_client()
    if not client:
        raise RuntimeError("No Anthropic API key configured, caller should use fallback path")

    response = client.messages.create(
        model=settings.llm_model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text_blocks = [block.text for block in response.content if block.type == "text"]
    return "".join(text_blocks).strip()
