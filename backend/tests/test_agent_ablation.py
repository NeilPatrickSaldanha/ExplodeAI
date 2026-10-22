"""Every `breaks_if_removed` statement in the agents lesson, backed by a real run without that part."""

import pytest

from app.experiments.agent.ablation import ablate
from app.experiments.agent.pipeline import HARD_CAP, STAGES, AgentParams
from tests.conftest import validates

P = AgentParams()


def test_baseline_answers():
    b = ablate(P, None)
    assert b["status"] == "answered" and b["answer"]


def test_goal():
    a = ablate(P, "goal")
    assert a["status"] == "no_goal" and a["tool_calls"] == 0 and a["answer"] is None


def test_tools():
    a = ablate(P, "tools")
    assert a["tool_calls"] == 0 and "can't look anything up" in a["answer"]


def test_decide():
    a = ablate(P, "decide")
    assert a["status"] == "no_decision" and a["tool_calls"] == 0 and a["answer"] is None


def test_validate():
    a = ablate(P, "validate")
    assert a["invalid_calls"] == 0 and "couldn't find an order called 1001" in a["answer"]
    assert ablate(P, None)["invalid_calls"] == 1, "with validation, the bad ID is caught and fixed"


@validates("tools-run-in-application")
def test_execute():
    a = ablate(P, "execute")
    assert a["status"] == "step_limit" and a["tool_runs"] == 0 and len(set(a["calls"])) == 1


def test_observe():
    a = ablate(P, "observe")
    assert a["status"] == "step_limit" and a["tool_runs"] == a["steps"] and len(set(a["calls"])) == 1


def test_context():
    a = ablate(P, "context")
    assert a["status"] == "step_limit" and a["answer"] is None
    assert a["calls"][:4] == ["search_help_centre", "get_order"] * 2, "it goes round in circles"


def test_stop():
    a = ablate(P, "stop")
    assert a["status"] == "safety_cap" and a["steps"] == HARD_CAP and a["answer"], "it answered and kept going"


@pytest.mark.parametrize("stage", STAGES)
def test_every_stage_changes_the_outcome(stage):
    b, a = ablate(P, None), ablate(P, stage)
    assert (a["status"], a["answer"], a["steps"]) != (b["status"], b["answer"], b["steps"])
