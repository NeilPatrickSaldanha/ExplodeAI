"""CI gate: validate every lesson against the content schema and publishing rules.

Usage:  uv run python scripts/validate_content.py [--content-dir PATH]
Exit code 1 if any lesson has problems (missing citations, unknown sources,
unverified claims in a published lesson, failed passes, broken references).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import REPO_DIR  # noqa: E402
from app.content.loader import load_lessons, load_registry  # noqa: E402
from app.content.schema import validate_lesson  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--content-dir", type=Path, default=REPO_DIR / "content")
    args = parser.parse_args()

    registry = load_registry(args.content_dir)
    lessons = load_lessons(args.content_dir)
    failed = False
    for lesson in lessons.values():
        problems = validate_lesson(lesson, registry)
        passes = [c.verification for c in lesson.claims]
        done = sum(
            all(p.status in ("passed", "not_applicable") for p in (v.primary, v.cross_check, v.technical))
            for v in passes
        )
        print(f"[{lesson.status}] {lesson.id}: {done}/{len(passes)} claims fully verified")
        for p in problems:
            print(f"   ✗ {p}")
        failed |= bool(problems)
    print("content validation:", "FAILED" if failed else "ok")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
