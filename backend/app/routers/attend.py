from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlmodel import Session

from app.content.schema import Challenge
from app.db import ExperimentRun, get_session
from app.deps import experiment_limiter, learner_id
from app.experiments.attend import model as m
from app.experiments.attend import pipeline
from app.experiments.attend.ablation import ablate
from app.routers.lessons import get_lesson_or_404

router = APIRouter(prefix="/api/experiments/attend", tags=["experiments"])


@router.get("/config")
def config():
    return {
        "defaults": pipeline.AttendParams().model_dump(),
        "model": {"kind": "toy", "note": pipeline.NOTE, "d_model": m.D_MODEL,
                  "head_choices": list(m.HEAD_CHOICES),
                  "max_tokens": m.MAX_TOKENS},
        "stages": pipeline.STAGES,
        "stage_dependencies": pipeline.STAGE_DEPENDENCIES,
    }


@router.post("/run")
def run(params: pipeline.AttendParams, learner: str = Depends(learner_id),
        session: Session = Depends(get_session)):
    experiment_limiter.check(learner)
    result = pipeline.run(params)
    session.add(ExperimentRun(learner_id=learner, experiment_id="attention", params=result["params"],
                              summary={"mean_max_weight": result["stats"]["mean_max_weight"],
                                       "future_mass": result["stats"]["future_mass"]}))
    session.commit()
    return result


class AblationRequest(pipeline.AttendParams):
    stage: str


@router.post("/ablate")
def ablate_stage(req: AblationRequest, learner: str = Depends(learner_id)):
    """Run the layer twice for real: as configured, and with one step removed."""
    experiment_limiter.check(learner)
    params = pipeline.AttendParams.model_validate(req.model_dump(exclude={"stage"}))
    try:
        return {"baseline": ablate(params, None), "ablated": ablate(params, req.stage)}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


def evaluate_challenge(challenge: Challenge, result: dict) -> dict:
    stats = result["stats"]
    checks = []
    for check in challenge.checks:
        if check.type == "no_future_attention":
            ok = stats["future_mass"] <= 1e-9
            msg = "No word attends to a later word." if ok else (
                f"Words still put {stats['future_mass']:.0%} of their attention on later words.")
        elif check.type == "not_saturated":
            limit = (check.limit or 80) / 100
            ok = stats["mean_max_weight"] < limit
            msg = (f"The strongest weight averages {stats['mean_max_weight']:.0%}, "
                   f"below {limit:.0%}: attention "
                   "is spread over several words." if ok else
                   f"The strongest weight averages {stats['mean_max_weight']:.0%}: softmax is almost "
                   "one-hot, so each word looks at a single word.")
        else:  # order_matters
            ok = stats["order_gap"] > 0.05
            msg = ("Reordering the words changes the output, so the layer can tell word order." if ok else
                   "Reordering the words changes nothing: the layer treats the sentence as a bag of words.")
        checks.append({"type": check.type, "gold": "", "passed": ok, "message": msg})
    return {"passed": all(c["passed"] for c in checks), "checks": checks}


@router.post("/challenges/{lesson_id}/{challenge_id}/check")
def check_challenge(lesson_id: str, challenge_id: str, params: dict, learner: str = Depends(learner_id)):
    experiment_limiter.check(learner)
    lesson = get_lesson_or_404(lesson_id)
    if lesson.experiment.get("engine") != "attend":
        raise HTTPException(404, "this lesson has no attention challenges")
    challenge = next((c for c in lesson.challenges if c.id == challenge_id), None)
    if challenge is None:
        raise HTTPException(404, "challenge not found")
    merged = {**params, **{k: challenge.broken_params[k] for k in challenge.locked_params}}
    try:
        p = pipeline.AttendParams.model_validate(merged)
    except ValidationError as exc:
        raise HTTPException(422, exc.errors(include_url=False)) from exc
    result = pipeline.run(p)
    return {**evaluate_challenge(challenge, result), "result": result}
