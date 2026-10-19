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
    # 30 chars → 10 tokens at $1/M, plus the full 100-token output allowance at $5/M.
    assert estimate_cost(PRICE, "x" * 30, 100) == pytest.approx((10 * 1 + 100 * 5) / 1e6)


def test_shipped_pricing_file_allows_nothing():
    load_prices.cache_clear()
    assert load_prices() == {}


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
