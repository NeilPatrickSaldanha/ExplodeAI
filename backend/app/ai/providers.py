"""Thin HTTP clients for paid providers. Only ever called after `guard.authorize`.

Keys are read from Settings at call time, sent only in request headers to the
provider's own API host, and never logged or returned. The request shapes follow
each provider's public REST API; they are exercised in tests with a mocked
transport and have NOT been exercised against the live APIs (that would cost
money and requires the owner's explicit permission).
"""

import httpx

from app.config import Settings


class ProviderError(Exception):
    pass


def _request(settings: Settings, provider: str, model: str, prompt: str, max_tokens: int):
    if provider == "anthropic":
        return (
            "https://api.anthropic.com/v1/messages",
            {
                "x-api-key": settings.anthropic_api_key.get_secret_value(),
                "anthropic-version": "2023-06-01",
            },
            {"model": model, "max_tokens": max_tokens,
             "messages": [{"role": "user", "content": prompt}]},
        )
    if provider == "openai":
        return (
            "https://api.openai.com/v1/chat/completions",
            {"authorization": f"Bearer {settings.openai_api_key.get_secret_value()}"},
            {"model": model, "max_completion_tokens": max_tokens,
             "messages": [{"role": "user", "content": prompt}]},
        )
    if provider == "gemini":
        return (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            {"x-goog-api-key": settings.gemini_api_key.get_secret_value()},
            {"contents": [{"parts": [{"text": prompt}]}],
             "generationConfig": {"maxOutputTokens": max_tokens}},
        )
    raise ProviderError(f"unknown provider {provider}")


def _extract_text(provider: str, data: dict) -> str:
    try:
        if provider == "anthropic":
            return "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")
        if provider == "openai":
            return data["choices"][0]["message"]["content"] or ""
        return "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderError("unexpected provider response shape") from exc


def generate(
    settings: Settings,
    provider: str,
    model: str,
    prompt: str,
    max_tokens: int,
    transport: httpx.BaseTransport | None = None,
) -> str:
    url, headers, body = _request(settings, provider, model, prompt, max_tokens)
    timeout = httpx.Timeout(settings.ai_request_timeout_seconds)
    with httpx.Client(timeout=timeout, transport=transport) as client:
        resp = client.post(url, headers=headers, json=body)
    if resp.status_code >= 400:
        # Never echo the response body: some providers reflect request headers.
        raise ProviderError(f"{provider} returned HTTP {resp.status_code}")
    return _extract_text(provider, resp.json())
