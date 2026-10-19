"""Pass 3 gate. Runs last (file name sorts last). Covers every lesson.

- Claim ids are unique across lessons, because @validates(claim_id) is not
  namespaced by lesson.
- Every claim whose technical pass is `passed` or `pending` must have at least
  one test decorated with @validates(claim_id).
- Every claim marked technically `passed` must have had at least one of those
  tests actually run AND pass in this session (skipped tests don't count —
  e.g. neural-embedding evidence needs `uv sync --extra neural`).
"""

from collections import Counter

import pytest

from app.config import REPO_DIR
from app.content.loader import load_lessons
from tests.conftest import PASSED_CLAIMS, VALIDATED_CLAIMS

LESSONS = load_lessons(REPO_DIR / "content")


def test_claim_ids_are_unique_across_lessons():
    counts = Counter(c.id for lesson in LESSONS.values() for c in lesson.claims)
    assert [cid for cid, n in counts.items() if n > 1] == []


def test_validated_ids_exist():
    ids = {c.id for lesson in LESSONS.values() for c in lesson.claims}
    assert set(VALIDATED_CLAIMS) <= ids, set(VALIDATED_CLAIMS) - ids


@pytest.mark.parametrize("lesson_id", sorted(LESSONS))
def test_every_checkable_claim_has_technical_evidence(lesson_id):
    missing = [
        c.id for c in LESSONS[lesson_id].claims
        if c.verification.technical.status in ("passed", "pending") and c.id not in VALIDATED_CLAIMS
    ]
    assert missing == [], f"{lesson_id}: claims with no Pass 3 test: {missing}"


@pytest.mark.parametrize("lesson_id", sorted(LESSONS))
def test_technically_passed_claims_have_passing_evidence_this_run(lesson_id):
    unproven = [
        c.id for c in LESSONS[lesson_id].claims
        if c.verification.technical.status == "passed" and c.id not in PASSED_CLAIMS
    ]
    assert unproven == [], (
        f"{lesson_id}: claims marked technically passed without a passing test this run: {unproven}. "
        "If tests were skipped, install extras: uv sync --extra neural"
    )
