# Educational content schema

Defined in [`backend/app/content/schema.py`](../backend/app/content/schema.py).
Lessons live in `content/lessons/<id>/lesson.yaml`; sources in `content/sources.yaml`.

## Source (`sources.yaml`)

| field | notes |
|---|---|
| `id` | referenced by citations |
| `title`, `publisher`, `authors` | |
| `url` | must be a valid URL |
| `type` | `paper` · `official_docs` · `official_blog` · `framework_docs` · `reference` |
| `version` | **required for papers** (arXiv version, proceedings); docs record "last updated" or "live page at access date" |
| `accessed` | date the research pass read it |

## Lesson

| section | purpose |
|---|---|
| `status` | `draft` or `published`; the validator blocks publishing until every claim passes |
| `claims[]` | atomic technical statements; each has `kind` (`fact` · `definition` · `provider_specific` · `simplification`), optional `provider`, ≥ 1 `citations` (source id, locator, excerpt ≤ 30 words), and `verification.{primary, cross_check, technical}` |
| `components[]` | parts of the exploded view: `id` (= pipeline stage id), label, phase, short/detail text, `claims` it teaches, geometry, assembled `position`, `explode` offset |
| `components[].explain` | beginner-friendly depth for the stage, kept in `explain.yaml` beside `lesson.yaml` and merged by the loader: `what`, `why`, `analogy`, `happens` (steps), `goes_to`, an illustrative `example` (input → steps → output), `misconfigured`, `learn_more` (technical), and `claims` (must be among the stage's own claims). Facts restate verified claims; analogies and examples are labelled as teaching aids. The validator requires one for every stage |
| `connections[]` | data-flow links between components (must equal the stage dependency graph) |
| `visuals[]` | every visual declares `real_execution`, `simulation`, or `conceptual` |
| `experiment` | presets and corpus note for the real experiment |
| `challenges[]` | break/fix tasks: `broken_params`, `locked_params`, `checks` (`gold_in_retrieved` / `gold_in_prompt`), hint, explanation |
| `reconstruction` | dependency graph for the rebuild puzzle (any topological order is correct) |
| `tour[]` | guided steps, each tied to a component and claims |

## Verification pass record

```yaml
verification:
  primary:     {status: passed, date: 2026-10-18, by: "pass1/deep-research"}
  cross_check: {status: passed, date: 2026-10-18, by: "pass2/independent-cross-check", notes: "..."}
  technical:   {status: passed, date: 2026-10-18, by: "pass3/pytest", notes: "Evidence: test_name"}
```

`status` is one of `pending`, `passed`, `failed`, `not_applicable`. Only the
technical pass may be `not_applicable`, and it must say why (for example, "needs
paid model calls" or "historical fact about a paper"). `passed` requires a date and
an author.

## Validator rules (CI gate)

`uv run python scripts/validate_content.py` fails when:

- a citation names an unknown source, or a claim has no citation;
- an excerpt exceeds 30 words;
- a provider-specific claim doesn't name its provider;
- any pass is `failed` (in any lesson, draft or not);
- a published lesson has any pass that isn't `passed` / `not_applicable`;
- a component, challenge, or tour step references an unknown claim, or a claim is unused;
- connections reference unknown components, or reconstruction dependencies don't match the components;
- a paper source lacks a version.

The backend test suite adds two more rules (`tests/test_zz_claim_coverage.py`):
every technically checkable claim has a test decorated with `@validates(claim_id)`,
and every claim marked technically `passed` had such a test actually run and pass
in that session (skipped tests don't count).
