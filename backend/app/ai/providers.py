"""Thin HTTP clients for paid providers. Only ever called after `guard.authorize`.

Keys are read from Settings at call time, sent only in request headers to the
provider's own API host, and never logged or returned. The request shapes follow
each provider's public REST API; they are exercised in tests with a mocked
transport. OpenAI and Gemini were also verified with one live call each on
2026-10-19 (owner-approved, $4 cap). Anthropic has not been called live.
"""

from dataclasses import dataclass

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


def _extract_usage(provider: str, data: dict) -> tuple[int, int] | None:
    """(input_tokens, output_tokens) as reported by the provider, or None."""
    try:
        if provider == "anthropic":
            u = data["usage"]
            return int(u["input_tokens"]), int(u["output_tokens"])
        if provider == "openai":
            u = data["usage"]
            return int(u["prompt_tokens"]), int(u["completion_tokens"])
        u = data["usageMetadata"]
        out = int(u.get("candidatesTokenCount", 0)) + int(u.get("thoughtsTokenCount", 0))
        return int(u["promptTokenCount"]), out
    except (KeyError, TypeError, ValueError):
        return None


@dataclass(frozen=True)
class Generation:
    text: str
    input_tokens: int | None
    output_tokens: int | None


def generate_with_usage(
    settings: Settings,
    provider: str,
    model: str,
    prompt: str,
    max_tokens: int,
    transport: httpx.BaseTransport | None = None,
) -> Generation:
    url, headers, body = _request(settings, provider, model, prompt, max_tokens)
    timeout = httpx.Timeout(settings.ai_request_timeout_seconds)
    with httpx.Client(timeout=timeout, transport=transport) as client:
        resp = client.post(url, headers=headers, json=body)
    if resp.status_code >= 400:
        # Never echo the response body: some providers reflect request headers.
        raise ProviderError(f"{provider} returned HTTP {resp.status_code}")
    data = resp.json()
    usage = _extract_usage(provider, data)
    return Generation(_extract_text(provider, data), *(usage or (None, None)))


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
