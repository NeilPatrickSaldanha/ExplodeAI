from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlmodel import Session

from app.content.schema import Challenge
from app.db import ExperimentRun, get_session
from app.deps import experiment_limiter, learner_id
from app.experiments.embed import model as bge
from app.experiments.embed import pipeline
from app.experiments.embed.ablation import ablate
from app.experiments.embed.corpus import SAMPLE_LIBRARY_ID, SAMPLE_LIBRARY_NOTE
from app.routers.lessons import get_lesson_or_404

router = APIRouter(prefix="/api/experiments/embed", tags=["experiments"])


def _ready() -> None:
    if not bge.neural_ready():
        raise HTTPException(503, "The embeddings lesson needs the local neural model: uv sync --extra neural")


@router.get("/config")
def config():
    return {
        "defaults": pipeline.EmbedParams().model_dump(),
        "neural_ready": bge.neural_ready(),
        "model": {"name": bge.MODEL_NAME, "build": bge.MODEL_BUILD, "max_tokens": bge.MAX_TOKENS,
                  "query_instruction": bge.QUERY_INSTRUCTION},
        "library": {"id": SAMPLE_LIBRARY_ID, "note": SAMPLE_LIBRARY_NOTE},
        "stages": pipeline.STAGES,
        "stage_dependencies": pipeline.STAGE_DEPENDENCIES,
    }


@router.post("/run")
def run(params: pipeline.EmbedParams, learner: str = Depends(learner_id),
        session: Session = Depends(get_session)):
    experiment_limiter.check(learner)
    _ready()
    result = pipeline.run(params)
    session.add(ExperimentRun(learner_id=learner, experiment_id="embeddings", params=result["params"],
                              summary={"neighbours": [n["id"] for n in result["neighbours"]],
                                       "comparable": result["comparable"]}))
    session.commit()
    return result


class AblationRequest(pipeline.EmbedParams):
    stage: str


@router.post("/ablate")
def ablate_stage(req: AblationRequest, learner: str = Depends(learner_id)):
    """Run the pipeline twice for real: as configured, and with one stage removed."""
    experiment_limiter.check(learner)
    _ready()
    params = pipeline.EmbedParams.model_validate(req.model_dump(exclude={"stage"}))
    try:
        return {"baseline": ablate(params, None), "ablated": ablate(params, req.stage)}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


def evaluate_challenge(challenge: Challenge, result: dict) -> dict:
    checks = []
    for check in challenge.checks:
        if check.type == "comparable":
            ok = result["comparable"]
            checks.append({"type": check.type, "gold": "", "passed": ok,
                           "message": "Query and library vectors come from the same model."
                           if ok else "Query and library vectors come from different models."})
        else:
            top = result["neighbours"][0] if result["neighbours"] else None
            for gold in check.gold:
                ok = bool(top) and top["category"] == gold and top["score"] > 0
                got = f"{top['category']} ({top['id']}, score {top['score']})" if top else "nothing"
                checks.append({"type": check.type, "gold": gold, "passed": ok,
                               "message": f"Top match is {got}; expected {gold}."})
    return {"passed": all(c["passed"] for c in checks), "checks": checks}


@router.post("/challenges/{lesson_id}/{challenge_id}/check")
def check_challenge(lesson_id: str, challenge_id: str, params: dict, learner: str = Depends(learner_id)):
    experiment_limiter.check(learner)
    _ready()
    lesson = get_lesson_or_404(lesson_id)
    if lesson.experiment.get("engine") != "embed":
        raise HTTPException(404, "this lesson has no embeddings challenges")
    challenge = next((c for c in lesson.challenges if c.id == challenge_id), None)
    if challenge is None:
        raise HTTPException(404, "challenge not found")
    merged = {**params, **{k: challenge.broken_params[k] for k in challenge.locked_params}}
    try:
        p = pipeline.EmbedParams.model_validate(merged)
    except ValidationError as exc:
        raise HTTPException(422, exc.errors(include_url=False)) from exc
    result = pipeline.run(p)
    return {**evaluate_challenge(challenge, result), "result": result}
