from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlmodel import Session

from app.content.schema import Challenge
from app.db import ExperimentRun, get_session
from app.deps import experiment_limiter, learner_id
from app.experiments.rag import pipeline
from app.experiments.rag.ablation import ablate
from app.experiments.rag.corpus import SAMPLE_CORPUS_ID, SAMPLE_CORPUS_NOTE, get_corpus
from app.experiments.rag.embedding import neural_available
from app.routers.lessons import get_lesson_or_404

router = APIRouter(prefix="/api/experiments/rag", tags=["experiments"])


@router.get("/config")
def config():
    schema = pipeline.RagParams.model_json_schema()
    return {
        "defaults": pipeline.RagParams().model_dump(),
        "schema": schema["properties"],
        "corpus": {
            "id": SAMPLE_CORPUS_ID,
            "note": SAMPLE_CORPUS_NOTE,
            "documents": [{"id": d.id, "title": d.title} for d in get_corpus()],
        },
        "embedders": [
            {"id": "lexical-hashing", "available": True,
             "label": "TF-IDF hashing (lexical, built in)"},
            {"id": "neural-local", "available": neural_available(),
             "label": "Local neural model (optional install)"},
        ],
        "stages": pipeline.STAGES,
        "stage_dependencies": pipeline.STAGE_DEPENDENCIES,
    }


def _run(params: pipeline.RagParams) -> dict:
    try:
        return pipeline.run(params)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/run")
def run(
    params: pipeline.RagParams,
    learner: str = Depends(learner_id),
    session: Session = Depends(get_session),
):
    experiment_limiter.check(learner)
    result = _run(params)
    session.add(
        ExperimentRun(
            learner_id=learner,
            experiment_id="rag-pipeline",
            params=result["params"],
            summary={
                "chunks": len(result["chunks"]),
                "retrieved": [r["chunk_id"] for r in result["retrieved"]],
                "dropped": result["prompt"]["dropped"],
            },
        )
    )
    session.commit()
    return result


def evaluate_challenge(challenge: Challenge, result: dict) -> dict:
    texts = {c["id"]: c["text"] for c in result["chunks"]}
    retrieved = [texts[r["chunk_id"]] for r in result["retrieved"]]
    prompt_text = result["prompt"]["text"]
    checks = []
    for check in challenge.checks:
        for gold in check.gold:
            if check.type == "gold_in_retrieved":
                ok = any(gold.lower() in t.lower() for t in retrieved)
                where = "a retrieved chunk"
            else:
                ok = gold.lower() in prompt_text.lower()
                where = "the assembled prompt"
            checks.append({"type": check.type, "gold": gold, "passed": ok,
                           "message": f"“{gold}” {'is' if ok else 'is not'} in {where}."})
    return {"passed": all(c["passed"] for c in checks), "checks": checks}


@router.post("/challenges/{lesson_id}/{challenge_id}/check")
def check_challenge(
    lesson_id: str,
    challenge_id: str,
    params: dict,
    learner: str = Depends(learner_id),
):
    experiment_limiter.check(learner)
    lesson = get_lesson_or_404(lesson_id)
    if lesson.experiment.get("engine") != "rag":
        raise HTTPException(404, "this lesson has no RAG challenges")
    challenge = next((c for c in lesson.challenges if c.id == challenge_id), None)
    if challenge is None:
        raise HTTPException(404, "challenge not found")
    # Locked params are forced back to the broken value: the learner must fix the
    # problem with the controls the challenge leaves open.
    merged = {**params, **{k: challenge.broken_params[k] for k in challenge.locked_params}}
    try:
        rag_params = pipeline.RagParams.model_validate(merged)
    except ValidationError as exc:
        raise HTTPException(422, exc.errors(include_url=False)) from exc
    result = _run(rag_params)
    return {**evaluate_challenge(challenge, result), "result": result}


class AblationRequest(pipeline.RagParams):
    stage: str


@router.post("/ablate")
def ablate_stage(req: AblationRequest, learner: str = Depends(learner_id)):
    """Run the pipeline twice for real: as configured, and with one stage removed."""
    experiment_limiter.check(learner)
    params = pipeline.RagParams.model_validate(req.model_dump(exclude={"stage"}))
    try:
        return {"baseline": ablate(params, None), "ablated": ablate(params, req.stage)}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
