"""Agent experiment: the loop, the tools, argument checks, approval and the challenges."""

import pytest

from app.experiments.agent import policy
from app.experiments.agent import tools as t
from app.experiments.agent.pipeline import HARD_CAP, STAGES, AgentParams, count_tokens, run
from tests.conftest import validates

H = {"X-Learner-Id": "agent-test-learner"}


def calls(r: dict) -> list[str]:
    return [s["decision"]["tool"] for s in r["steps"] if s.get("decision") and s["decision"]["tool"]]


def test_stages_match_the_lesson_components():
    from app.content.loader import content

    lesson = content()[1]["agents"]
    assert [c.id for c in lesson.components] == STAGES


@validates("tool-definition")
def test_every_tool_has_a_name_description_and_json_schema():
    for d in t.definitions():
        assert d["name"] and d["description"] and d["input_schema"]["type"] == "object"
        assert set(d["input_schema"]["required"]) <= set(d["input_schema"]["properties"])


@validates("agent-loop", "tool-errors-are-results", "mcp-human-in-loop")
def test_default_run_finds_the_order_fixes_a_bad_id_and_waits_for_approval():
    r = run(AgentParams())
    assert calls(r) == ["search_help_centre", "get_order", "get_order", "days_between", "issue_refund"]
    bad = r["steps"][1]
    assert bad["decision"]["arguments"] == {"order_id": "1001"} and bad["validation"]["errors"]
    assert bad["execution"]["ran"] is False and bad["observation"]["is_error"] is True
    assert r["steps"][2]["decision"]["arguments"] == {"order_id": "A1001"}, "it reads the error and retries"
    assert r["status"] == "needs_approval" and r["held"]["tool"] == "issue_refund" and r["refunds"] == []


@validates("agent-loop", "tool-result-linked")
def test_approved_run_answers_from_tool_results_only():
    r = run(AgentParams(approve=True))
    assert r["status"] == "answered" and len(r["refunds"]) == 1
    a = r["answer"]
    assert "16 days ago" in a and "within 30 days" in a and "R-001" in a and "2,899.00 CAD" in a
    # every result is linked to the call that asked for it
    # each result sits straight after the call it answers and carries that call's id
    msgs = r["messages"]
    pairs = [(msgs[i], msgs[i + 1]) for i in range(len(msgs) - 1) if msgs[i].get("kind") == "tool_call"]
    assert pairs and all(res["role"] == "tool" and res["tool_call_id"] == call["id"] for call, res in pairs)


@pytest.mark.parametrize(
    "goal,expect",
    [
        ("Can I return order A1002?", "can no longer be returned"),
        ("I want to return order A1003", "custom-built bikes cannot be returned"),
        ("Can I return order A1004?", "hasn't been delivered yet"),
        ("Where is my order A1004?", "is shipped"),
        ("Can I return order A9999?", "couldn't find an order called A9999"),
        ("How long do refunds take?", "within 5 business days"),
        ("How long does the battery take to charge?", "4.5 hours"),
    ],
)
def test_answers_follow_the_data(goal, expect):
    r = run(AgentParams(goal=goal))
    assert r["status"] == "answered" and expect in r["answer"]


@validates("tools-run-in-application")
def test_the_model_never_runs_tools_the_application_does():
    r = run(AgentParams(approve=True))
    runs = [s for s in r["steps"] if (s.get("execution") or {}).get("ran")]
    assert len(runs) == r["stats"]["tool_runs"] == 4
    assert all(s["decision"]["kind"] == "tool_call" for s in runs)


@validates("validate-tool-inputs")
def test_validation_rejects_bad_arguments():
    schema = t.SCHEMAS["get_order"]
    assert t.validate(schema, {"order_id": "A1001"}) == []
    assert t.validate(schema, {"order_id": "1001"})
    assert t.validate(schema, {}) == ["missing required argument 'order_id'"]
    assert t.validate(schema, {"order_id": 1001}) == ["'order_id' must be a string"]
    assert t.validate(t.SCHEMAS["issue_refund"], {"order_id": "A1001", "amount": -5})
    assert t.validate(schema, {"order_id": "A1001", "extra": 1}) == ["unknown argument 'extra'"]


@validates("validate-tool-inputs")
def test_without_validation_a_bad_id_reaches_the_tool():
    r = run(AgentParams(validate_args=False))
    assert r["status"] == "answered" and "couldn't find an order called 1001" in r["answer"]


@validates("tool-errors-are-results")
def test_a_tool_failure_comes_back_as_an_error_result_not_a_crash():
    out = t.execute("days_between", {"start": "not a date", "end": "2026-10-21"}, poisoned=False, ledger=[])
    assert out.is_error and "not a date" in out.content["error"]
    assert t.execute("no_such_tool", {}, poisoned=False, ledger=[]).is_error


@validates("context-resent", "tool-tokens-billed")
def test_context_grows_every_step_and_is_re_read_each_time():
    r = run(AgentParams(approve=True))
    per_step = [s["tokens_in"] for s in r["steps"]]
    assert per_step == sorted(per_step) and len(set(per_step)) == len(per_step)
    assert r["stats"]["tokens_total"] == sum(per_step) > per_step[-1] * 3
    # tool definitions alone cost tokens before the first message
    assert run(AgentParams(), "tools")["steps"][0]["tokens_in"] < per_step[0]
    assert count_tokens("hello") > 0


@validates("stopping-conditions")
def test_vague_descriptions_pick_the_wrong_tool_and_the_step_limit_stops_it():
    r = run(AgentParams(descriptions="vague"))
    assert calls(r)[1] == "search_help_centre", "it searched the help centre for an order number"
    assert r["status"] == "step_limit" and r["stats"]["steps"] == 8 and r["answer"] is None


@validates("stopping-conditions")
def test_without_a_step_limit_only_the_hard_cap_stops_a_stuck_loop():
    r = run(AgentParams(descriptions="vague", max_steps=None))
    assert r["status"] == "safety_cap" and r["stats"]["steps"] == HARD_CAP
    limited = run(AgentParams(descriptions="vague", max_steps=8))
    assert r["stats"]["tokens_total"] > 5 * limited["stats"]["tokens_total"]


def test_tool_choice_comes_from_the_descriptions():
    detailed = policy.score_tools("look up the customer order by its order ID", t.definitions("detailed"))
    best = max(detailed, key=lambda s: s["score"])
    assert best["tool"] == "get_order"
    vague = policy.score_tools("look up the customer order by its order ID", t.definitions("vague"))
    assert len({s["score"] for s in vague}) == 1, "vague descriptions give every tool the same score"


@validates("indirect-injection")
def test_injected_instructions_in_a_tool_result_move_money_without_approval():
    r = run(AgentParams(goal="What is your returns policy?", poisoned_doc=True, require_approval=False))
    assert calls(r) == ["search_help_centre", "issue_refund"]
    assert r["stats"]["unapproved_side_effects"] == 1 and r["refunds"][0]["amount"] == 2899.0


@validates("owasp-excessive-agency", "mcp-human-in-loop")
def test_approval_or_least_privilege_stops_the_injected_refund():
    guarded = run(AgentParams(goal="What is your returns policy?", poisoned_doc=True))
    assert guarded["status"] == "needs_approval" and guarded["refunds"] == []
    no_tool = run(AgentParams(goal="What is your returns policy?", poisoned_doc=True, require_approval=False,
                              refund_tool=False))
    assert no_tool["refunds"] == [] and no_tool["stats"]["unapproved_side_effects"] == 0
    assert "issue_refund" not in {d["name"] for d in no_tool["tools"]}


def test_the_poisoned_page_is_off_by_default():
    r = run(AgentParams(goal="What is your returns policy?", require_approval=False))
    assert r["refunds"] == [] and "issue_refund" not in calls(r)


def test_runs_are_repeatable():
    a, b = run(AgentParams()), run(AgentParams())
    assert a["messages"] == b["messages"] and a["stats"] == b["stats"]


@validates("agent-workflow-vs-agent")
def test_the_same_loop_takes_different_paths_for_different_goals():
    paths = {g: tuple(calls(run(AgentParams(goal=g)))) for g in (
        "Can I return order A1002?", "Where is my order A1004?", "How long do refunds take?")}
    assert len(set(paths.values())) == 3, paths
    assert paths["Where is my order A1004?"] == ("get_order",)


@validates("mcp-human-in-loop")
def test_a_side_effect_waits_for_a_person_and_runs_only_after_approval():
    held = run(AgentParams())
    assert held["status"] == "needs_approval" and held["refunds"] == [] and held["stats"]["tool_runs"] == 3
    done = run(AgentParams(approve=True))
    assert len(done["refunds"]) == 1 and done["stats"]["unapproved_side_effects"] == 0
    assert [s for s in done["steps"] if s["decision"] and s["decision"]["tool"] == "issue_refund"][0][
        "execution"]["approved_by_person"] is True


# --- API ---


def test_config_and_run_endpoints(client):
    cfg = client.get("/api/experiments/agent/config").json()
    assert cfg["stages"] == STAGES and cfg["model"]["kind"] == "stand_in" and len(cfg["orders"]) == 4
    r = client.post("/api/experiments/agent/run", json={}, headers=H).json()
    assert r["status"] == "needs_approval"
    assert client.post("/api/experiments/agent/run", json={"goal": "x" * 301}, headers=H).status_code == 422
    assert client.post("/api/experiments/agent/run", json={"max_steps": 99}, headers=H).status_code == 422


def test_ablation_endpoint(client):
    r = client.post("/api/experiments/agent/ablate", json={"stage": "observe"}, headers=H).json()
    assert r["baseline"]["status"] == "answered" and r["ablated"]["status"] == "step_limit"
    assert client.post("/api/experiments/agent/ablate", json={"stage": "nope"}, headers=H).status_code == 422


def _challenge(client, cid, params):
    return client.post(f"/api/experiments/agent/challenges/agents/{cid}/check", json=params, headers=H).json()


def test_challenges_fail_when_broken_and_pass_when_fixed(client):
    from app.content.loader import content

    lesson = content()[1]["agents"]
    fixes = {
        "runaway-loop": {"max_steps": 8},
        "vague-tools": {"descriptions": "detailed"},
        "injected-refund": {"require_approval": True},
    }
    assert {c.id for c in lesson.challenges} == set(fixes)
    for ch in lesson.challenges:
        broken = _challenge(client, ch.id, ch.broken_params)
        assert broken["passed"] is False, ch.id
        fixed = _challenge(client, ch.id, {**ch.broken_params, **fixes[ch.id]})
        assert fixed["passed"] is True, (ch.id, fixed["checks"])
