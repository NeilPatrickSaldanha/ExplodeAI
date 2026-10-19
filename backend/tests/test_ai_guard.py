"""The paid-AI guard must fail closed. No test here touches the network."""

from datetime import UTC, datetime

import httpx
import pytest
from pydantic import SecretStr
from sqlmodel import Session

from app.ai import providers
from app.ai.guard import GuardRefusal, ModelPrice, authorize, estimate_cost, load_prices
from app.config import Settings, get_settings
from app.db import AIUsage

PRICE = ModelPrice(provider="anthropic", model="test-model", input_usd_per_million_tokens=1.0,
                   output_usd_per_million_tokens=5.0, price_checked="2026-10-18",
                   price_source="https://example.invalid/pricing")
PRICES = {("anthropic", "test-model"): PRICE}
FAKE_KEY = "sk-test-NOT-A-REAL-KEY-123"


def settings(**kw) -> Settings:
    base = dict(ai_features_enabled=True, anthropic_api_key=SecretStr(FAKE_KEY),
                ai_daily_budget_usd=1.0, ai_max_requests_per_hour=2, ai_max_output_tokens=300)
    return Settings(_env_file=None, **{**base, **kw})


def call(s, session, **kw):
    args = dict(learner_id="l-00000001", provider="anthropic", model="test-model",
                prompt="hello", max_output_tokens=100, confirm_paid=True, prices=PRICES)
    return authorize(s, session, **{**args, **kw})


@pytest.mark.parametrize("overrides,call_kw,code", [
    ({"ai_emergency_disable": True}, {}, "emergency_disabled"),
    ({"ai_features_enabled": False}, {}, "disabled"),
    ({"anthropic_api_key": SecretStr("")}, {}, "no_key"),
    ({}, {"model": "unlisted"}, "model_not_allowed"),
    ({}, {"confirm_paid": False}, "not_confirmed"),
    ({}, {"max_output_tokens": 301}, "too_many_tokens"),
    ({}, {"provider": "mystery"}, "unknown_provider"),
])
def test_guard_refusals(engine, overrides, call_kw, code):
    with Session(engine) as session, pytest.raises(GuardRefusal) as exc:
        call(settings(**overrides), session, **call_kw)
    assert exc.value.code == code


def test_kill_switch_beats_everything(engine):
    with Session(engine) as session, pytest.raises(GuardRefusal) as exc:
        call(settings(ai_emergency_disable=True, ai_features_enabled=False), session)
    assert exc.value.code == "emergency_disabled"


def test_rate_limit_and_budget(engine):
    s = settings()
    now = datetime.now(UTC)
    with Session(engine) as session:
        assert call(s, session).estimated_cost_usd > 0
        for _ in range(2):
            session.add(AIUsage(learner_id="l-00000001", provider="anthropic", model="test-model",
                                estimated_cost_usd=0.001, status="ok", created_at=now))
        session.commit()
        with pytest.raises(GuardRefusal) as exc:
            call(s, session)
        assert exc.value.code == "rate_limited"
        session.add(AIUsage(learner_id="other-000001", provider="anthropic", model="test-model",
                            estimated_cost_usd=0.9995, status="ok", created_at=now))
        session.commit()
        with pytest.raises(GuardRefusal) as exc:
            call(s, session, learner_id="l-00000002")
        assert exc.value.code == "budget_exceeded"


def test_cost_estimate_is_worst_case():
    # 30 chars → 15 tokens at $1/M, plus the full 100-token output allowance at $5/M.
    assert estimate_cost(PRICE, "x" * 30, 100) == pytest.approx((15 * 1 + 100 * 5) / 1e6)


def test_shipped_pricing_file_is_sourced_and_dated():
    load_prices.cache_clear()
    prices = load_prices()
    assert prices, "allow-list should name at least one model"
    for price in prices.values():
        assert price.price_source.startswith("https://") and price.price_checked
        assert price.input_usd_per_million_tokens > 0 and price.output_usd_per_million_tokens > 0


def test_default_settings_disable_paid_ai():
    s = Settings(_env_file=None)
    assert s.ai_features_enabled is False
    assert s.ai_emergency_disable is False


def test_provider_client_with_mock_transport_sends_key_only_in_header():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["host"] = request.url.host
        seen["key"] = request.headers["x-api-key"]
        seen["body"] = request.content.decode()
        return httpx.Response(200, json={"content": [{"type": "text", "text": "hi"}]})

    out = providers.generate(settings(), "anthropic", "test-model", "prompt", 10,
                             transport=httpx.MockTransport(handler))
    assert out == "hi"
    assert seen["host"] == "api.anthropic.com"
    assert seen["key"] == FAKE_KEY and FAKE_KEY not in seen["body"]


def test_provider_errors_never_echo_response_body():
    def handler(request):
        return httpx.Response(401, text=f"bad key {FAKE_KEY}")

    with pytest.raises(providers.ProviderError) as exc:
        providers.generate(settings(), "anthropic", "m", "p", 10, transport=httpx.MockTransport(handler))
    assert FAKE_KEY not in str(exc.value)


def test_status_endpoint_reveals_presence_not_keys(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "anthropic_api_key", SecretStr(FAKE_KEY))
    r = client.get("/api/ai/status")
    assert r.status_code == 200
    assert FAKE_KEY not in r.text
    body = r.json()
    assert body["providers"]["anthropic"]["key_configured"] is True
    assert body["enabled"] is False


def test_generate_endpoint_refuses_by_default(client):
    r = client.post("/api/ai/generate", json={"provider": "anthropic", "model": "x",
                                              "prompt": "hi", "confirm_paid": True})
    assert r.status_code == 403
    assert r.json()["detail"]["code"] == "disabled"


def test_total_budget_is_enforced_across_days(engine):
    s = settings(ai_total_budget_usd=0.01, ai_daily_budget_usd=100)
    with Session(engine) as session:
        session.add(AIUsage(learner_id="old-learner-01", provider="anthropic", model="test-model",
                            estimated_cost_usd=0.0099, status="ok",
                            created_at=datetime(2020, 1, 1, tzinfo=UTC)))
        session.commit()
        with pytest.raises(GuardRefusal) as exc:
            call(s, session)
        assert exc.value.code == "total_budget_exceeded"


@pytest.mark.parametrize("provider,body,expected", [
    ("anthropic", {"content": [{"type": "text", "text": "a"}], "usage": {"input_tokens": 11, "output_tokens": 7}}, (11, 7)),
    ("openai", {"choices": [{"message": {"content": "a"}}], "usage": {"prompt_tokens": 11, "completion_tokens": 7}}, (11, 7)),
    ("gemini", {"candidates": [{"content": {"parts": [{"text": "a"}]}}],
                "usageMetadata": {"promptTokenCount": 11, "candidatesTokenCount": 5, "thoughtsTokenCount": 2}}, (11, 7)),
])
def test_usage_is_read_from_each_provider(provider, body, expected):
    s = settings(openai_api_key=SecretStr(FAKE_KEY), gemini_api_key=SecretStr(FAKE_KEY))
    gen = providers.generate_with_usage(s, provider, "m", "p", 10,
                                        transport=httpx.MockTransport(lambda r: httpx.Response(200, json=body)))
    assert (gen.text, gen.input_tokens, gen.output_tokens) == ("a", *expected)


def _enable(monkeypatch):
    from app.ai import guard

    s = get_settings()
    monkeypatch.setattr(s, "ai_features_enabled", True)
    monkeypatch.setattr(s, "anthropic_api_key", SecretStr(FAKE_KEY))
    monkeypatch.setattr(guard, "load_prices", lambda: PRICES)
    import app.routers.ai as ai_router
    monkeypatch.setattr(ai_router, "load_prices", lambda: PRICES)


def test_rag_answer_builds_the_prompt_server_side_and_ledgers_actual_cost(client, engine, monkeypatch):
    _enable(monkeypatch)
    seen = {}

    def fake(settings_, provider, model, prompt, max_tokens):
        seen["prompt"] = prompt
        return providers.Generation("Within 30 days.", 150, 12)

    monkeypatch.setattr(providers, "generate_with_usage", fake)
    body = {"query": "How long do I have to return a bike?", "provider": "anthropic", "model": "test-model",
            "confirm_paid": True, "max_output_tokens": 200}
    r = client.post("/api/ai/rag-answer", json=body, headers={"X-Learner-Id": "learner-0001"})
    assert r.status_code == 200, r.text
    out = r.json()
    assert seen["prompt"].startswith("<documents>") and "Question: How long" in seen["prompt"]
    assert out["cost_usd"] == pytest.approx((150 * 1.0 + 12 * 5.0) / 1e6)
    assert out["cost_usd"] <= out["max_cost_usd"]
    with Session(engine) as session:
        assert session.exec(__import__("sqlmodel").select(AIUsage)).one().estimated_cost_usd == pytest.approx(0.00021)


def test_rag_answer_requires_confirmation(client, monkeypatch):
    _enable(monkeypatch)
    r = client.post("/api/ai/rag-answer", json={"provider": "anthropic", "model": "test-model"})
    assert r.status_code == 403 and r.json()["detail"]["code"] == "not_confirmed"


def test_rag_answer_estimate_is_free(client, monkeypatch, engine):
    _enable(monkeypatch)
    r = client.post("/api/ai/rag-answer/estimate", json={"provider": "anthropic", "model": "test-model"})
    assert r.status_code == 200 and 0 < r.json()["max_cost_usd"] < 0.01
    with Session(engine) as session:
        assert session.exec(__import__("sqlmodel").select(AIUsage)).all() == []
