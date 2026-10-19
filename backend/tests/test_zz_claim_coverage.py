"""Pass 3 gate. Runs last (file name sorts last).

- Every claim whose technical pass is `passed` or `pending` must have at least
  one test decorated with @validates(claim_id).
- Every claim marked technically `passed` must have had at least one of those
  tests actually run AND pass in this session (skipped tests don't count —
  e.g. neural-embedding evidence needs `uv sync --extra neural`).
"""

from app.config import REPO_DIR
from app.content.loader import load_lessons
from tests.conftest import PASSED_CLAIMS, VALIDATED_CLAIMS


def test_every_checkable_claim_has_technical_evidence():
    lesson = load_lessons(REPO_DIR / "content")["rag-pipeline"]
    missing = [
        c.id for c in lesson.claims
        if c.verification.technical.status in ("passed", "pending") and c.id not in VALIDATED_CLAIMS
    ]
    assert missing == [], f"claims with no Pass 3 test: {missing}"


def test_validated_ids_exist():
    lesson = load_lessons(REPO_DIR / "content")["rag-pipeline"]
    ids = {c.id for c in lesson.claims}
    assert set(VALIDATED_CLAIMS) <= ids, set(VALIDATED_CLAIMS) - ids


def test_technically_passed_claims_have_passing_evidence_this_run():
    lesson = load_lessons(REPO_DIR / "content")["rag-pipeline"]
    unproven = [
        c.id for c in lesson.claims
        if c.verification.technical.status == "passed" and c.id not in PASSED_CLAIMS
    ]
    assert unproven == [], (
        f"claims marked technically passed without a passing test this run: {unproven}. "
        "If tests were skipped, install extras: uv sync --extra neural"
    )
