"""What breaks if one part of the agent loop is removed? Run the real loop without it.

- goal      no goal, so there is nothing to work on and no action is taken.
- tools     no tool definitions: the agent cannot look anything up, so it replies without the
            order or the policy.
- decide    nothing chooses the next action, so no tool is ever called and no answer is given.
- validate  bad arguments reach the tool: "1001" is looked up as written, no order matches, and
            the agent reports that the order does not exist instead of correcting the ID.
- execute   tool calls are made but nothing runs them, so no result ever comes back and the agent
            asks for the same thing until the step limit stops it.
- observe   tools run but their results are not passed back, so the agent repeats the same call
            (and the tool runs again each time) until the step limit stops it.
- context   the agent only sees the goal and the latest result, so it forgets what it already
            found and goes round in circles until the step limit stops it.
- stop      nothing checks for a final answer or a step limit, so the loop keeps going after it has
            answered, until the experiment's own hard cap stops it.

Both runs use the learner's settings, with the refund pre-approved so the loop can reach its end.
These statements describe ExplodeAI's own loop and are checked by tests/test_agent_ablation.py.
"""

from app.experiments.agent.pipeline import STAGES, AgentParams, run

NOTES = {
    "goal": "no goal, so there is nothing to work on",
    "tools": "no tools, so it answers without looking anything up",
    "decide": "nothing chooses an action, so nothing happens",
    "validate": "arguments are not checked, so a bad order ID goes straight to the tool",
    "execute": "calls are made, but nothing runs them",
    "observe": "tools run, but their results never come back",
    "context": "it only remembers the goal and the latest result",
    "stop": "nothing ends the loop, not even its own answer",
}


def summary(r: dict) -> dict:
    return {
        "status": r["status"],
        "answer": r["answer"],
        "steps": r["stats"]["steps"],
        "tool_calls": r["stats"]["tool_calls"],
        "tool_runs": r["stats"]["tool_runs"],
        "invalid_calls": r["stats"]["invalid_calls"],
        "tokens_total": r["stats"]["tokens_total"],
        "calls": [s["decision"]["tool"] for s in r["steps"] if s.get("decision") and s["decision"]["tool"]],
    }


def ablate(params: AgentParams, stage: str | None) -> dict:
    if stage is not None and stage not in STAGES:
        raise ValueError(f"unknown stage '{stage}'")
    p = params.model_copy(update={"approve": True})
    out = summary(run(p, stage))
    return {"removed": stage, **out, "notes": [NOTES[stage]] if stage else []}
