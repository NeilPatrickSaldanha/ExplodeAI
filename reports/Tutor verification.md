# Ask ExplodeAI (tutor) verification

Verification record for the grounded tutor (`backend/app/tutor/`, `backend/app/routers/tutor.py`,
`frontend/src/tutor/`). Completed 2026-10-20.

> The tutor is not a lesson, so it has no claims of its own. What it can say is limited to
> content that already passed three verification passes, and the checks below measure that
> limit rather than assume it.

## What it can say, and why that is safe

- **Only lesson content is indexed:** 120+ verified claims and the stage explanations, tours,
  challenge write-ups and objectives of the four lessons, about 470 passages. Nothing else.
- **Default answers are extractive:** the free answer quotes sentences from those passages and
  attaches the verified claims and sources behind each. No model writes it, so nothing can be invented.
  A test checks that every returned sentence is a substring of an indexed passage.
- **Relevance is gated:** a question the lessons do not cover returns no sentences, no claims and no
  sources, and the tutor says so.
- **Analogies are labelled** "teaching aid, not a verified fact" and never counted as facts.
- **Tutor mode** asks about the open stage from its own explanation (5 questions per stage, 160
  across the lessons) and reveals the lesson's answer. It does not grade you.

## Measured retrieval quality

`backend/tests/test_tutor_eval.py` on a fixed set (`tests/tutor_eval_set.py`): 30 in-scope
questions, each with the stage(s) that should answer it, and 13 out-of-scope questions.

| | Hybrid (BM25 + local neural model) | Keyword only (no neural extra) |
|---|---|---|
| In-scope questions answered (covered) | 30 / 30 | 30 / 30 |
| Right stage in the top 3 | 30 / 30 | 27 / 30 |
| Right stage first | 25 / 30 | 23 / 30 |
| Out-of-scope questions wrongly answered | 0 / 13 | 1 / 13 ("How do I lose weight?" matches the word "weight") |
| Instruction-like and junk input ("ignore the lessons…", SQL-looking text, gibberish) | refused (4 / 4) | not guaranteed |

The gate combines two signals: a question is covered if it is clearly close in meaning to a lesson
passage, or every meaningful word appears in the lessons and the meaning is at least roughly close,
or most words appear and the meaning is clearly close. Thresholds were set from the numbers above
and are pinned by the eval test, so a change cannot silently make retrieval worse.

**Known limits.** Without the local neural model the tutor falls back to keyword matching, which can
be fooled by words shared with the lessons; the panel says "keyword matching only" when that
happens. The first-ranked passage is not always the best one (25 of 30), though the right stage is
always in the top three. Extractive answers can read as a collage of quotes rather than a single
explanation, which is why the optional polish exists.

## The optional paid polish

- The server builds the prompt from the retrieved passages only; the client cannot send a prompt.
- It goes through the same guard, ledger, budget, rate limit and kill switch as every paid feature,
  and is refused by default.
- A question the lessons do not cover makes no provider call and costs nothing; the estimate
  endpoint is free.
- The model is told to cite claim ids; any citation to a claim that was not in the prompt is stripped
  and the answer is flagged as not fully grounded.
- Tested only against mocked HTTP. **No live paid call was made for this feature.**

## Automated gates

Backend tests `test_tutor.py` (17) and `test_tutor_eval.py` (3), end-to-end `tutor.spec.ts` (6) and a
phone test, all passing alongside the full suites (ruff, backend, 31 unit, 54 end-to-end tests).
