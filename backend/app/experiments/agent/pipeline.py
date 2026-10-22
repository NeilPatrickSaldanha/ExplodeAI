"""The agent loop, run for real: decide → validate → (approve) → execute → observe, until it stops.

The stage ids are the contract between this code, the lesson content
(`content/lessons/agents/lesson.yaml` components) and the 3D view.

What is real and what is not:
- the loop, argument validation, the tools and the token counts run for real;
- the tools work on FICTIONAL data (Ridgeline Bikes, from Lesson 01);
- the decision-maker is a stand-in rule, not a language model (see policy.py).
"""

import json
import time
from functools import lru_cache

from pydantic import BaseModel, Field

from app.experiments.agent import policy
from app.experiments.agent import tools as t

STAGE_DEPENDENCIES: dict[str, list[str]] = {
    # One pass round the loop. After the first pass, "decide" also reads the context built by earlier passes;
    # that loop-back is the connection context → decide, not a dependency, so the order stays runnable.
    "goal": [],
    "tools": [],
    "decide": ["goal", "tools"],
    "validate": ["decide"],
    "execute": ["validate"],
    "observe": ["execute"],
    "context": ["observe"],
    "stop": ["decide"],
}
STAGES = list(STAGE_DEPENDENCIES)

HARD_CAP = 30  # the experiment's own safety net, separate from the agent's step limit
NOTE = (
    "The decisions come from a short stand-in rule, not a language model, so the run is free and the "
    "same every time. The loop, the argument checks, the tools and the token counts are real; the shop "
    "and its orders are made up."
)
SYSTEM = (
    "You are Ridgeline Bikes' support agent. Answer the customer using the tools. Use only what the "
    "tools return. Today is " + t.TODAY.isoformat() + "."
)
TOKEN_LABEL = "Counted with Lesson 02's teaching tokenizer, not any provider's, so real counts differ."

DEFAULT_GOAL = "Hi! I'd like to return my E-Trail from order 1001. Can I get a refund?"


class AgentParams(BaseModel):
    goal: str = Field(DEFAULT_GOAL, min_length=3, max_length=300)
    descriptions: t.Descriptions = "detailed"
    validate_args: bool = True
    max_steps: int | None = Field(8, ge=1, le=20)  # None: no step limit (only the hard cap stops it)
    require_approval: bool = True
    approve: bool = False  # a person approves the held action
    refund_tool: bool = True
    poisoned_doc: bool = False


@lru_cache(maxsize=1)
def _tokenizer():
    from app.experiments.tokenize import pipeline as tok
    from app.experiments.tokenize.corpus import SAMPLE_CORPUS_ID

    return tok._full_training(SAMPLE_CORPUS_ID, "bytes", "words")


@lru_cache(maxsize=4096)
def count_tokens(text: str) -> int:
    return len(_tokenizer().encode(text))


def _ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 3)


def _dump(m: dict) -> str:
    return json.dumps(m, ensure_ascii=False, sort_keys=True)


def run(p: AgentParams, skip: str | None = None) -> dict:
    """Run the agent. `skip` removes one stage (used by the ablation)."""
    available = [] if skip == "tools" else t.definitions(p.descriptions, p.refund_tool)
    fixed_tokens = count_tokens(SYSTEM) + count_tokens(json.dumps(available, sort_keys=True))
    goal_msg = {"role": "user", "content": p.goal}
    messages: list[dict] = [goal_msg] if skip != "goal" else []
    steps: list[dict] = []
    ledger: list[dict] = []
    timings = dict.fromkeys(STAGES, 0.0)
    status, answer, held = "running", None, None
    executions = 0
    no_stop = skip == "stop"
    limit = None if no_stop else p.max_steps
    n = 0
    while True:
        n += 1
        if n > HARD_CAP:
            status = "safety_cap"
            break
        if limit is not None and n > limit:
            status = "step_limit"
            break
        start = time.perf_counter()
        # Without context the agent only sees the goal and the most recent call and result.
        visible = [*messages[:1], *messages[1:][-2:]] if skip == "context" else list(messages)
        tokens_in = fixed_tokens + sum(count_tokens(_dump(m)) for m in visible)
        timings["context"] += _ms(start)
        step: dict = {"index": n, "tokens_in": tokens_in, "visible_messages": len(visible)}
        steps.append(step)

        if skip in ("decide", "goal"):
            step["decision"] = None
            status = "no_decision" if skip == "decide" else "no_goal"
            break
        start = time.perf_counter()
        d = policy.decide(p.goal, visible, available)
        timings["decide"] += _ms(start)
        step["decision"] = {
            "kind": d.kind,
            "reason": d.reason,
            "tool": d.tool,
            "arguments": d.arguments,
            "scores": d.scores,
        }

        if d.kind == "final":
            messages.append({"role": "assistant", "kind": "final", "content": d.answer})
            answer = d.answer
            if no_stop:  # nothing checks for the final answer, so the loop just goes round again
                continue
            status = "answered"
            break

        call_id = f"call_{n}"
        messages.append(
            {
                "role": "assistant",
                "kind": "tool_call",
                "id": call_id,
                "tool": d.tool,
                "arguments": d.arguments,
            }
        )
        schema = next(x["input_schema"] for x in available if x["name"] == d.tool)

        start = time.perf_counter()
        errors = t.validate(schema, d.arguments) if skip != "validate" and p.validate_args else []
        timings["validate"] += _ms(start)
        step["validation"] = {"checked": skip != "validate" and p.validate_args, "errors": errors}
        if errors:
            out = t.ToolOutput({"error": "; ".join(errors)}, is_error=True)
            step["execution"] = {"ran": False, "reason": "invalid arguments"}
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "tool": d.tool,
                    "content": out.content,
                    "is_error": True,
                }
            )
            step["observation"] = {"returned": True, "is_error": True, "content": out.content}
            continue

        if d.tool in t.SIDE_EFFECTS and p.require_approval and not p.approve:
            held = {"tool": d.tool, "arguments": d.arguments}
            step["execution"] = {"ran": False, "reason": "waiting for a person to approve"}
            status = "needs_approval"
            break

        start = time.perf_counter()
        if skip == "execute":
            out = None
            step["execution"] = {"ran": False, "reason": "nothing runs the tool"}
        else:
            out = t.execute(d.tool, d.arguments, poisoned=p.poisoned_doc, ledger=ledger)
            executions += 1
            step["execution"] = {
                "ran": True,
                "ms": _ms(start),
                "is_error": out.is_error,
                "approved_by_person": d.tool in t.SIDE_EFFECTS and p.require_approval,
            }
        timings["execute"] += _ms(start)

        start = time.perf_counter()
        if out is not None and skip != "observe":
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "tool": d.tool,
                    "content": out.content,
                    "is_error": out.is_error,
                }
            )
            step["observation"] = {"returned": True, "is_error": out.is_error, "content": out.content}
        else:
            step["observation"] = {"returned": False, "content": out.content if out else None}
        timings["observe"] += _ms(start)

    tool_steps = [s for s in steps if s.get("decision") and s["decision"]["kind"] == "tool_call"]
    unapproved = [r for r in ledger if not p.require_approval]
    return {
        "params": p.model_dump(),
        "model": {
            "kind": "stand_in",
            "note": NOTE,
            "today": t.TODAY.isoformat(),
            "hard_cap": HARD_CAP,
            "token_label": TOKEN_LABEL,
        },
        "system": SYSTEM,
        "tools": available,
        "steps": steps,
        "messages": messages,
        "status": status,
        "answer": answer,
        "held": held,
        "refunds": ledger,
        "stats": {
            "steps": len(steps),
            "tool_calls": len(tool_steps),
            "tool_runs": executions,
            "invalid_calls": sum(1 for s in tool_steps if s.get("validation", {}).get("errors")),
            "tokens_last": steps[-1]["tokens_in"] if steps else 0,
            "tokens_total": sum(s["tokens_in"] for s in steps),
            "unapproved_side_effects": len(unapproved),
            "answered": status == "answered",
        },
        "timings_ms": {k: round(v, 3) for k, v in timings.items()},
        "stages": STAGES,
    }
