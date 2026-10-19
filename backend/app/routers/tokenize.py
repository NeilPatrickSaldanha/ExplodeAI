from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlmodel import Session

from app.content.schema import Challenge
from app.db import ExperimentRun, get_session
from app.deps import experiment_limiter, learner_id
from app.experiments.tokenize import pipeline
from app.experiments.tokenize.corpus import SAMPLE_CORPUS
from app.routers.lessons import get_lesson_or_404

router = APIRouter(prefix="/api/experiments/tokenize", tags=["experiments"])


@router.get("/config")
def config():
    schema = pipeline.TokenizeParams.model_json_schema()
    return {
        "defaults": pipeline.TokenizeParams().model_dump(),
        "schema": schema["properties"],
        "max_merges": pipeline.MAX_MERGES,
        "label": pipeline.LABEL,
        "corpus": {"id": SAMPLE_CORPUS.id, "title": SAMPLE_CORPUS.title, "note": SAMPLE_CORPUS.note},
        "stages": pipeline.STAGES,
        "stage_dependencies": pipeline.STAGE_DEPENDENCIES,
    }


def _run(params: pipeline.TokenizeParams) -> dict:
    try:
        return pipeline.run(params)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/run")
def run(
    params: pipeline.TokenizeParams,
    learner: str = Depends(learner_id),
    session: Session = Depends(get_session),
):
    experiment_limiter.check(learner)
    result = _run(params)
    session.add(
        ExperimentRun(
            learner_id=learner,
            experiment_id="tokenization",
            params=result["params"],
            summary={
                "merges_learned": result["training"]["merges_learned"],
                "vocab_size": result["vocabulary"]["size"],
                "tokens": result["encoding"]["count"],
                "round_trip": result["decoding"]["round_trip"],
            },
        )
    )
    session.commit()
    return result


def evaluate_challenge(challenge: Challenge, result: dict) -> dict:
    tokens = [t["text"] for t in result["encoding"]["tokens"]]
    checks = []

    def add(check_type: str, ok: bool, message: str, gold: str = "") -> None:
        checks.append({"type": check_type, "gold": gold, "passed": ok, "message": message})

    for check in challenge.checks:
        if check.type == "round_trip":
            ok = result["decoding"]["round_trip"]
            add(check.type, ok, "Decoding the tokens gives back exactly the input text." if ok
                else "Decoding the tokens does not give back the input text.")
        elif check.type == "no_unknown":
            n = result["decoding"]["unk_count"]
            add(check.type, n == 0, "No token is [UNK]." if n == 0 else f"{n} token(s) are [UNK].")
        elif check.type == "max_tokens":
            n = result["encoding"]["count"]
            ok = n <= check.limit
            add(check.type, ok, f"The text is {n} tokens; the budget is {check.limit}.")
        elif check.type == "single_token":
            for gold in check.gold:
                ok = gold in tokens
                add(check.type, ok, f"“{gold}” {'is' if ok else 'is not'} a single token.", gold)
        elif check.type == "no_cross_word_tokens":
            crossing = result["vocabulary"]["crossing_word_boundary"]
            add(check.type, not crossing,
                "No learned token spans two words." if not crossing
                else f"{len(crossing)} learned token(s) span a word boundary, e.g. “{crossing[0]}”.")
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
    if lesson.experiment.get("engine") != "tokenize":
        raise HTTPException(404, "this lesson has no tokenization challenges")
    challenge = next((c for c in lesson.challenges if c.id == challenge_id), None)
    if challenge is None:
        raise HTTPException(404, "challenge not found")
    # Locked params are forced back to the broken value: the learner must fix the
    # problem with the controls the challenge leaves open.
    merged = {**params, **{k: challenge.broken_params[k] for k in challenge.locked_params}}
    try:
        tok_params = pipeline.TokenizeParams.model_validate(merged)
    except ValidationError as exc:
        raise HTTPException(422, exc.errors(include_url=False)) from exc
    result = _run(tok_params)
    return {**evaluate_challenge(challenge, result), "result": result}

