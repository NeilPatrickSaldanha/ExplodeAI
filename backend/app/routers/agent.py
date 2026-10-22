from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlmodel import Session

from app.content.schema import Challenge
from app.db import ExperimentRun, get_session
from app.deps import experiment_limiter, learner_id
from app.experiments.agent import pipeline
from app.experiments.agent import tools as t
from app.experiments.agent.ablation import ablate
from app.routers.lessons import get_lesson_or_404

router = APIRouter(prefix="/api/experiments/agent", tags=["experiments"])


@router.get("/config")
def config():
    return {
        "defaults": pipeline.AgentParams().model_dump(),
        "model": {
            "kind": "stand_in",
            "note": pipeline.NOTE,
            "hard_cap": pipeline.HARD_CAP,
            "today": t.TODAY.isoformat(),
            "token_label": pipeline.TOKEN_LABEL,
        },
        "orders": [{"order_id": k, **v} for k, v in t.ORDERS.items()],
        "stages": pipeline.STAGES,
        "stage_dependencies": pipeline.STAGE_DEPENDENCIES,
    }


@router.post("/run")
def run(
    params: pipeline.AgentParams, learner: str = Depends(learner_id), session: Session = Depends(get_session)
):
    experiment_limiter.check(learner)
    result = pipeline.run(params)
    session.add(
        ExperimentRun(
            learner_id=learner,
            experiment_id="agents",
            params=result["params"],
            summary={"status": result["status"], "steps": result["stats"]["steps"]},
        )
    )
    session.commit()
    return result


class AblationRequest(pipeline.AgentParams):
    stage: str


@router.post("/ablate")
def ablate_stage(req: AblationRequest, learner: str = Depends(learner_id)):
    """Run the loop twice for real: as configured, and with one part removed."""
    experiment_limiter.check(learner)
    params = pipeline.AgentParams.model_validate(req.model_dump(exclude={"stage"}))
    try:
        return {"baseline": ablate(params, None), "ablated": ablate(params, req.stage)}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


def evaluate_challenge(challenge: Challenge, result: dict) -> dict:
    stats = result["stats"]
    checks = []
    for check in challenge.checks:
        if check.type == "stops_within":
            limit = check.limit or 10
            ok = stats["steps"] <= limit
            msg = (
                f"The loop stopped after {stats['steps']} steps, within {limit}."
                if ok
                else f"The loop ran {stats['steps']} steps (limit for this check: {limit}) and re-read "
                f"{stats['tokens_total']:,} tokens in total."
            )
        elif check.type == "answer_contains":
            answer = result["answer"] or ""
            missing = [g for g in check.gold if g.lower() not in answer.lower()]
            ok = result["status"] == "answered" and not missing
            msg = (
                "The agent answered with the facts it needed."
                if ok
                else "The agent never answered."
                if result["status"] != "answered"
                else f"The answer is missing: {', '.join(missing)}."
            )
        else:  # no_unapproved_side_effects
            ok = stats["unapproved_side_effects"] == 0
            msg = (
                "No money moved without a person approving it."
                if ok
                else f"{stats['unapproved_side_effects']} refund(s) went out with nobody approving them."
            )
        checks.append({"type": check.type, "gold": ", ".join(check.gold), "passed": ok, "message": msg})
    return {"passed": all(c["passed"] for c in checks), "checks": checks}


@router.post("/challenges/{lesson_id}/{challenge_id}/check")
def check_challenge(lesson_id: str, challenge_id: str, params: dict, learner: str = Depends(learner_id)):
    experiment_limiter.check(learner)
    lesson = get_lesson_or_404(lesson_id)
    if lesson.experiment.get("engine") != "agent":
        raise HTTPException(404, "this lesson has no agent challenges")
    challenge = next((c for c in lesson.challenges if c.id == challenge_id), None)
    if challenge is None:
        raise HTTPException(404, "challenge not found")
    merged = {**params, **{k: challenge.broken_params[k] for k in challenge.locked_params}}
    try:
        p = pipeline.AgentParams.model_validate(merged)
    except ValidationError as exc:
        raise HTTPException(422, exc.errors(include_url=False)) from exc
    result = pipeline.run(p)
    return {**evaluate_challenge(challenge, result), "result": result}
