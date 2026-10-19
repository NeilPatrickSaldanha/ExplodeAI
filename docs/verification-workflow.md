# Research and verification workflow

Every published lesson goes through three independent passes. The workflow
produces inspectable evidence; it does **not** guarantee absolute correctness.

## Pass 1 — primary-source research

- Run with the `deep-research` skill: parallel researchers, each scoped to one
  subtopic and told to prioritise original papers and official provider docs
  (Anthropic, OpenAI, Google, Hugging Face, FAISS, etc.).
- Output: `research_notes/<title>/*.md` (findings with URL, version or date, and
  a ≤ 25-word excerpt, plus a claims table with confidence) and a synthesised
  `reports/<title>.md`.
- Lesson authors write claims only from these notes, and record
  `primary: passed` with the date.

## Pass 2 — independent factual cross-check

- A separate agent that didn't write the lesson reads `lesson.yaml` and
  `sources.yaml` and, **for every claim**:
  1. re-fetches the cited source and string-matches each excerpt against the raw text;
  2. checks that the source supports the claim *as worded* (scope, numbers, hedging);
  3. finds at least one additional authoritative source that isn't already cited;
  4. flags dated or provider-specific details.
- It also reviews non-claim lesson text (component details, challenge explanations, tour bodies).
- Output: `research_notes/<title>/pass2_cross_check.md`, with a verdict per claim
  (`confirmed`, `confirmed_with_changes`, `disputed`, `unverifiable`) and a
  machine-readable YAML block.
- Authors apply every fix and record `cross_check: passed` with a note on what
  changed. A `disputed` claim passes only after it has been rewritten from the
  source and re-checked.

## Pass 3 — technical validation

- Executable evidence in the backend suite. Tests decorated with
  `@validates("claim-id")` check algorithmic claims (cosine = dot product for unit
  vectors, BM25 saturation and `b = 0`, the RRF formula, exact flat search, overlap
  preserving boundary facts, swapping the corpus to update knowledge) and semantic
  claims, using a real local neural embedding model.
- Consistency checks make sure that diagrams and animations match the algorithm:
  the 3D components equal the executed pipeline stages, diagram edges equal the
  stage dependency graph, and every challenge fails when broken and passes with a
  known fix that uses only unlocked controls.
- Claims that can't be executed without paid calls, or that are historical facts
  about a paper, are `not_applicable` with a stated reason.

## Automated gates

- `scripts/validate_content.py` covers schema, citations, and the publishing rule.
- `tests/test_zz_claim_coverage.py` requires every claim marked technically
  `passed` to have had a passing test in this run.
- CI runs both on every push. A lesson with any unresolved issue stays `draft`,
  and the API hides drafts by default.

## Labels in the product

Every visual is labelled **Real execution**, **Simulation**, or **Conceptual**.
The offline answer step is labelled "Real execution, not an LLM". Each claim card
shows its three pass states and links to its sources.
