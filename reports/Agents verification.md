# Agents verification

Research and verification report for **Lesson 05 · Tool-using agents, exploded**
(`content/lessons/agents/lesson.yaml`, version 1.0.0, status **published**).
Completed 2026-10-22.

> Three verification passes give each claim recorded, inspectable evidence. They do
> not guarantee absolute correctness. Provider documentation changes often; every
> source records the date it was read.

## Summary

| | |
|---|---|
| Claims | 24 (13 provider-specific, each naming its provider) |
| Citations | 68 excerpts (each 30 words or fewer) from 15 registered sources: 4 papers, Anthropic, OpenAI and Google docs, the OpenAI Agents SDK docs, two OWASP pages and the MCP specification |
| Pass 1 (primary-source research) | 24/24 passed |
| Pass 2 (independent cross-check) | 10 confirmed · 14 confirmed with changes · 0 disputed · 0 unverifiable. All 58 original excerpts were found in the live pages; none was fabricated. All fixes applied, and all 68 final excerpts re-checked word for word |
| Pass 3 (technical validation) | 13 executed and passing · 11 not applicable, each with a reason |
| Automated gates | content validator ✓ · claim-coverage gate ✓ · 377 backend tests passing |

**What this lesson's model is.** The agent loop is ExplodeAI's own code. It really runs: the
decide, check, approve, run, observe and context steps, the tools, the argument validator,
the step limit and the token counts. Two things are **not** real. The *decision-maker* is a
short stand-in rule, not a language model (labelled a **simulation** wherever it appears), so runs are free
and repeatable. And the *shop* (Ridgeline Bikes, from Lesson 01) and its four orders are made up;
a refund only writes a line in that run's own list. No provider, paid API or key was used at any stage.
Token counts use Lesson 02's teaching tokenizer, so real counts differ.

## Pass 1 · primary-source research

Done with the `deep-research` skill, two runs plus direct reads of the pages the runs left open.
Synthesis: `reports/Agents primary sources.md`. Notes and raw outputs: `research_notes/Agents primary sources/`.

Caveats Pass 1 caught before any lesson text was written:
- A Gemini claim (tool definitions count as billed tokens) was refuted 0 to 3 and never used.
- Run 2 first failed on a usage limit and returned nothing; the rerun succeeded.
- OWASP's mitigations and the MCP specification were read directly, because the runs did not confirm them.
- The pages for Anthropic, OpenAI, Gemini and OWASP show no last-updated date, so the register says "live page at access date".

## Pass 2 · independent cross-check

A separate agent re-fetched every source (and downloaded each raw page to test every excerpt as an exact
substring), checked the claim text against the evidence, looked for independent sources, and compared the
lesson text with the code. Full report: `research_notes/Agents primary sources/pass2_cross_check.md`.

Changes applied:
- `tool-definition`: the Gemini page documents an OpenAPI-schema subset, not JSON Schema. Claim and the stage text now say so, and a `name` excerpt was added.
- `tool-choice`: "required" and "forced" are OpenAI's words, `any`/`tool` are Anthropic's, Gemini has its own modes, and forced use returns an error on several current Claude models. Claim rewritten with the caveat.
- `tools-run-in-application`: "Anthropic also offers server tools" implied only Anthropic does; now "Anthropic, for one".
- `tool-errors-are-results`: MCP treats unknown tools and bad arguments as protocol errors, not `isError` results. Claim says so.
- `tool-result-linked`: the OpenAI excerpt now contains `call_id`; locator fixed.
- `loop-stop-reason`: scoped to client tools (server tools use `pause_turn`).
- `indirect-injection`: Greshake et al. "argue" the data/instruction blur and "show" the code-execution effect; the text no longer says the first causes the second.
- `mrkl-origin`: "multiple neural models, including large language models", not "a language model".
- `tool-tokens-billed`: OpenAI's line covers definitions only; results are attributed to Anthropic.
- `injection-no-foolproof` and the stage text: "Nobody knows a foolproof way" replaced by OWASP's own "unclear whether".
- Five locators fixed; one weak excerpt dropped.
- Lesson text: "takes no step at all" became "does nothing"; the dashed-line legend now includes tool output; the vague-tools brief says "a few empty words"; "the only step that needs a model" became "in this loop"; the corpus note says no money moves; the token wording names the teaching tokenizer; the Stop stage mentions the approval pause; context text is scoped to a plain API loop; one uncited sentence was removed.
- Tests: a note that overstated a test was reworded and renamed; the call-and-result pairing test now checks each pair; the ablation test for "the model only asks" is tagged as evidence.

## Pass 3 · technical validation

Executed against the real loop (`backend/tests/test_agent.py`, `test_agent_ablation.py`):

| Claim | Test |
|---|---|
| agent-loop | A run goes goal, tool calls, results, answer; each result changes the next decision |
| agent-workflow-vs-agent | The same loop takes different paths for different goals |
| tool-definition | Every tool has a name, a description and a JSON Schema |
| tools-run-in-application | Decision and execution are separate; with the Run step removed, calls are made and never run |
| tool-result-linked | Every result sits after, and carries the id of, the call it answers |
| tool-errors-are-results | A rejected call and a failing tool both come back as results; the agent corrects the first |
| validate-tool-inputs | Bad type, missing, unknown and out-of-range arguments are rejected; with checking off, "1001" reaches the tool |
| stopping-conditions | A step limit ends a stuck loop; without one only the 30-step hard cap does |
| context-resent, tool-tokens-billed | Tokens read grow every step; tool definitions add to them |
| indirect-injection | A hidden instruction in a help-centre page makes the stand-in issue a refund |
| owasp-excessive-agency, mcp-human-in-loop | Approval, or removing the refund tool, stops the injected refund; a side effect waits for a person |
| (8 stages) | The loop run without each part fails in its own way, backing every `breaks_if_removed` statement |
| (3 challenges) | Each fails when broken and passes when fixed |

Not applicable (each with a reason in the lesson file): the three research papers, provider API options (`tool_choice`, `stop_reason`, the SDK's `max_turns`, context-window limits), provider guidance about real models (detailed tool descriptions, cost and error compounding), OWASP's statement that prompt-injection prevention is unproven, and the MCP tool primitive.

## Visual honesty

| Visual | Kind |
|---|---|
| Exploded view, data flow | Conceptual |
| Experiment, ablation | Real execution (the loop, tools, checks and token counts) |
| Stand-in decider | **Simulation**, never presented as a language model |

## Known limits

- The stand-in picks a tool by comparing descriptions and always obeys instructions it reads in a tool result. That makes the mechanisms visible; it says nothing about how often a real model is fooled.
- The argument checker covers a small subset of JSON Schema (type, required, pattern, length, minimum, unknown arguments).
- MCP was read at specification 2025-06-18; a newer version may exist.

## Gates at publication

- Content validator ✓, claim-coverage gate ✓, ruff ✓, 377 backend tests ✓, 39 frontend unit tests ✓, 127 end-to-end tests across all lessons ✓.
- 9 end-to-end tests for this lesson (3D render, real loop with approval, approval reset, checks off, runaway loop and token cost, conversation view, break & fix, ablation, tour) ✓.
- The tutor now knows all five lessons; code-like input is no longer matched against lesson text.
