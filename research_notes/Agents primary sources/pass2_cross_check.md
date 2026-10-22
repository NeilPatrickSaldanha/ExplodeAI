# Lesson 05 (agents), Pass 2 independent cross-check

Verifier: Pass 2 (independent). Date of checks: 2026-10-22. No lesson files, sources.yaml or code were edited.

## How the checks were done (and limits)

- Every cited page was fetched live. Five pages were read with WebFetch (Anthropic "Building effective agents" and the four arXiv abs pages). WebFetch only summarises, so for the exact-wording test I also downloaded the raw page of every source with curl (Anthropic docs and MCP spec came back as markdown, the rest as HTML), stripped tags, markdown, backticks, case and quote style, and tested each excerpt as an exact substring of the whole page with a script. All 12 non-arXiv sources and all 4 arXiv pages were covered this way. I did not read the 983 KB Gemini page or the two 360 KB OWASP pages by eye end to end; I searched them programmatically and read the surrounding text for every hit.
- Word counts of all 58 excerpts were computed: longest is 26 words (context-window-limit). None exceeds 30.
- The code was run: `uv`/venv python with `PYTHONPATH=.`; `pytest tests/test_agent.py tests/test_agent_ablation.py` gave 45 passed, 0 failed.

## Summary table

| Verdict | Count | Claims |
|---|---|---|
| Confirmed (no change needed) | 10 | agent-loop, react-origin, toolformer-origin, validate-tool-inputs, stopping-conditions, agents-cost-errors, context-window-limit, owasp-excessive-agency, mcp-tools-primitive, mcp-human-in-loop |
| Confirmed with changes | 14 | agent-workflow-vs-agent, mrkl-origin, tool-definition, tool-descriptions-matter, tool-choice, tools-run-in-application, tool-result-linked, loop-stop-reason, tool-errors-are-results, sdk-max-turns, context-resent, tool-tokens-billed, indirect-injection, injection-no-foolproof |
| Disputed | 0 | (strongest: tool-definition for Gemini, tool-choice model support) |
| Unverifiable | 0 | |

Excerpts: 58 checked, 0 NOT FOUND, 58 found (a few with trivial formatting differences, listed at the end). Locators: 7 do not name a real section (listed at the end).

---

## Part 1 and 2 and 3: claim by claim

### agent-workflow-vs-agent: CONFIRMED WITH CHANGES
- Excerpts: all 3 FOUND (page text is "Workflows are systems where LLMs and tools are orchestrated through predefined code paths." and "**Agents**, on the other hand, are systems where LLMs dynamically direct their own processes and tool usage, maintaining control over how they accomplish tasks."; "agentic systems" is bold on the page).
- Text is supported. Published 2024-12-19 (matches register).
- Locator "Workflows and agents" is not a heading. All three sentences are under "What are agents?".
- Technical note is overstated: "takes different paths for different goals, because it follows what the tools return". In policy.py the path is chosen by goal regexes (`needs_for`: `_RETURN`, `_ORDER_REF`) and fixed need lists; tool results only decide whether the days/refund needs appear. The test (`test_the_path_depends_on_what_the_tools_return_not_on_fixed_code`) only shows three goals give three paths. By Anthropic's own definition the stand-in is nearer a scripted workflow. Required change to the note: "The same loop code takes different paths for different goals (the stand-in's choices depend on the goal and on earlier results)." Rename the test too.
- Independent source: Anthropic "When (and when not) to use agents" section of the same article (same publisher); no other publisher consulted.

### agent-loop: CONFIRMED
- Both excerpts FOUND. "In the typical case" matches "typically just". Locator "Agents" is a real heading in Building blocks, workflows, and agents. Independent: OpenAI function-calling "tool calling flow" (five steps ending "or more tool calls") and OpenAI Agents SDK loop agree.

### react-origin: CONFIRMED
- Both excerpts FOUND in the abstract (arXiv v3, 10 Mar 2023, is the ICLR camera-ready; v1 was 6 Oct 2022, so "(2022)" is right). Register version string matches.

### toolformer-origin: CONFIRMED
- FOUND. Only v1 (9 Feb 2023) exists, matches register. Text drops "and how to best incorporate the results", which is fine.

### mrkl-origin: CONFIRMED WITH CHANGES
- Excerpt FOUND (v1, 1 May 2022, only version).
- Text says "pairs a language model with discrete knowledge and reasoning modules". The excerpt says "multiple neural models" (the title says large language models plus other things), not "a language model". Replacement: "The MRKL paper (2022) proposes a flexible architecture that combines multiple neural models (including large language models) with discrete knowledge and reasoning modules."

### tool-definition: CONFIRMED WITH CHANGES (closest to disputed)
- Excerpts: Anthropic FOUND (table row, with a markdown link on "JSON Schema"; locator "Specifying client tools (input_schema)" is the real heading "Specifying client tools"). OpenAI FOUND (`parameters` row; locator "Defining functions (parameters)" matches "Defining functions"). Gemini two excerpts FOUND.
- Problem: the text says all three write parameters "as a JSON Schema". The Gemini page never says JSON Schema. Its cited lines say only "Input parameters the function expects", and its notes say "only a subset of the OpenAPI schema is supported". Only Anthropic and OpenAI say JSON Schema.
- Also no excerpt supports "name" for any provider. Add the Anthropic table row for `name` and the OpenAI `name` row.
- Replacement text: "Anthropic, OpenAI and Gemini all describe a tool to the model with a name, a description and a schema for its parameters. Anthropic and OpenAI call it JSON Schema; Gemini uses a subset of the OpenAPI schema." Same fix in explain.yaml tools.learn_more ("the same way across providers ... JSON Schema" overstates; say "in a similar way").
- Technical note ("a JSON Schema") only tests `type == object` and required subset of properties; fine as stated.

### tool-descriptions-matter: CONFIRMED WITH CHANGES
- Excerpts 1 and 2 FOUND (Define tools, "Best practices for tool definitions"; also shows `input_examples` as a secondary aid, no conflict). Text matches ("at least 3–4 sentences").
- Excerpt 3 is FOUND but its locator "Prompt engineering your tools" is wrong: the sentence is in the "Summary" section (Appendix 2 is the prompt-engineering section). It only loosely supports the text ("thorough tool documentation"); it could be dropped.
- Independent: OpenAI "Best practices for defining functions" says write clear and detailed function names/parameter descriptions (agrees, but does not rank it "most important"). So "by far the most important" is Anthropic-only; the text already attributes it to Anthropic. Fine.

### tool-choice: CONFIRMED WITH CHANGES (important caveats)
- Excerpts all FOUND (Anthropic locator "Forcing tool use (tool_choice)" matches the last bullet list under "Forcing tool use"; OpenAI "Tool choice" matches).
- Issues:
  1. Names. Anthropic's modes are `auto`, `any`, `tool` (and `none`). OpenAI's are `auto`, `required`, forced function (and `allowed_tools`, `none`). "required" and "forced" are OpenAI wording. No cited OpenAI excerpt covers "required"; the OpenAI line is "Required: Call one or more functions." (one or more, not "one").
  2. Availability: Anthropic's page says forced use is not supported everywhere: with manual extended thinking `any` and `tool` error, and for Claude Opus 5.5, Sonnet 5.5, Fable 5.1 and Mythos 5.1 they return a 400 error (use `auto` plus strict tool use instead). The claim implies a universal option.
  3. Gemini also has modes (AUTO default, ANY "constrained to always predict a function call", NONE, VALIDATED, with `allowed_tools`), so "Anthropic and OpenAI" is true but incomplete.
- Replacement: "Anthropic, OpenAI and Gemini let the application set how free the model is: automatic (the model decides whether to call a tool), a mode that requires some tool call (Anthropic any, OpenAI required, Gemini ANY), or a named tool (Anthropic tool, OpenAI forced function). Not every model supports the required and forced modes." Add the OpenAI "Required" excerpt and the Anthropic "tool forces Claude to always use a particular tool" bullet. kind/provider "Anthropic/OpenAI" would become "Anthropic/OpenAI/Google" if Gemini is added.

### tools-run-in-application: CONFIRMED WITH CHANGES
- Excerpts FOUND. OpenAI one is a numbered list item with no final period on the page (and capital E) ; trivial. Anthropic "Server-executed tools" and "The tool-use contract" are real headings. Gemini locator "How function calling works" not checked as a heading name but the sentence is in that flow list.
- Misleading omission: "Anthropic also offers server tools" reads as Anthropic-only. OpenAI's page itself lists built-in tools (search the web, run code, MCP connectors) that OpenAI runs ("Functions versus tools"). Gemini's docs navigation lists Google Search, code execution tools (not verified on the page body). Same problem in explain.yaml execute.learn_more ("Anthropic, OpenAI and Gemini all leave the running to your application. Anthropic also offers server tools...").
- Replacement: "...Anthropic also offers server tools, which Anthropic runs for you; OpenAI and Gemini have built-in tools that they run too." 
- Technical note cites "removing execution leaves calls that never run": that is in test_agent_ablation.test_execute, not in the `@validates("tools-run-in-application")` test, which only shows runs happen after decisions. Add the ablation test to the evidence, otherwise accurate.

### tool-result-linked: CONFIRMED WITH CHANGES
- Anthropic excerpt FOUND (Python example, `tool_use_id`). Anthropic "Handle tool calls" also says "`tool_use_id`: The id of the tool use request this is a result for": correct attribution.
- OpenAI excerpt FOUND but it does not contain "call_id"; the page says the output "should contain a reference to a specific model tool call (referenced by `call_id` in the examples to come)". Add the parenthetical to the excerpt (still under 30 words). Locator "The function calling flow (call_id)" is wrong: the sentence is in "Tool call outputs - output we generate for the model".
- Independent: Gemini's interactions example sends `functionresult` with `call_id: fcstep.id`, so Gemini links results too. explain.observe.learn_more says "Each provider links a result to its call: OpenAI by call_id, Anthropic by the tool_use id": either add Gemini (`call_id`) or say "OpenAI and Anthropic".
- Technical note: test asserts result ids are a subset of call ids, which would pass if a result were linked to the wrong call. Correct pairing holds by construction in pipeline.py (same `call_id` used) but the test does not prove it. Strengthen test or soften note to "every result carries the id of some call".

### loop-stop-reason: CONFIRMED WITH CHANGES
- All 3 excerpts FOUND, real section "The agentic loop (client tools)".
- Add scope "for client tools": the same page also describes `pause_turn` for server tools (re-send the conversation to continue), and the context-windows page describes `model_context_window_exceeded`. "Exits on any other" is the page's wording for the client-tool loop.

### tool-errors-are-results: CONFIRMED WITH CHANGES
- Both excerpts FOUND under "Error Handling" ("Tool Execution Errors: Reported in tool results with isError: true" has bold/code markup on the page). Version 2025-06-18 correct.
- Caveat: the same section says protocol errors ("Unknown tools", "Invalid arguments", server errors) are standard JSON-RPC errors, not isError results. "Invalid input data" appears only as a Tool Execution Error example. The text's "invalid input" is therefore easy to misread, and ExplodeAI's Check step (schema rejection) corresponds more to MCP's "Invalid arguments" (protocol error) than to isError. Replacement: "In the Model Context Protocol a tool that fails while running, for example with an API failure or input its own logic rejects, reports the error in its result, flagged isError: true. Unknown tools and malformed requests are JSON-RPC protocol errors instead."
- Independent: Anthropic "Handle tool calls": `is_error: true` on a tool_result lets the model see the error. Agrees.
- Technical note: the test's error-then-retry is a validation error from ExplodeAI's own Check step, not a tool failure; the genuine tool failure is only tested by `test_a_tool_failure_comes_back...` (days_between). Note should say both.

### validate-tool-inputs: CONFIRMED
- Both excerpts FOUND ("Servers MUST: Validate all tool inputs"; OpenAI "Setting strict to true will ensure function calls reliably adhere to the function schema, instead of being best effort."). MCP says SHOULD for clients to validate tool results, MUST for servers to validate inputs: text matches. Note (not a conflict): OpenAI strict requires `additionalProperties: false` and all fields required, and the doc notes strict is disabled for multi-call on fine-tuned models.
- Technical: `validate()` is a subset (type, required, pattern, length, minimum, unknown args), not full JSON Schema; component text "against the tool's schema" is fine but could say "a simple subset of JSON Schema" in the tools.py sense.

### stopping-conditions: CONFIRMED
- FOUND (page uses a curly apostrophe in "it's"). Independent: OpenAI Agents SDK max_turns agrees.

### agents-cost-errors: CONFIRMED
- Both FOUND. 

### sdk-max-turns: CONFIRMED WITH CHANGES
- All 3 FOUND. Excerpt 3 locator "Runner options" is wrong: "Pass max_turns=None to disable this turn limit." sits in "The agent loop" (also repeated under Exceptions). Text accurate. The page also defines final output as text output with no tool calls and handoffs; text omits handoffs, acceptable.

### context-resent: CONFIRMED WITH CHANGES
- Both FOUND. "Contains all previous conversation history plus the current user message" is the "Input phase" bullet, in "How the context window works".
- Caveats from the same Anthropic pages: prompt caching "changes what you pay for those tokens, not whether they count"; server-side compaction and context editing (tool-result clearing) can shorten history. Also OpenAI (`previous_response_id`, `conversation_id`, per the Agents SDK page) and Gemini (`previous_interaction_id`) offer server-held state, so the application need not resend; the model still reads the history. The claim is scoped to Anthropic, so it holds; but tour/context texts ("The model has no memory of its own. Each step sends the whole conversation again") and explain.context.why are unscoped. Suggest "In a plain API loop, each step sends the whole conversation again" and, for "paid for, again" (context.detail), "paid for (at a reduced price if the provider caches the repeated start)".

### tool-tokens-billed: CONFIRMED WITH CHANGES
- All 3 FOUND (OpenAI "Token Usage" ; Anthropic "Pricing"). OpenAI's line covers definitions only; tool results are covered by Anthropic's pricing bullet and the context-window page, not OpenAI's. Attribute accordingly (provider field "OpenAI/Anthropic" is fine if the text says results are shown for Anthropic). Caching caveat as above.

### context-window-limit: CONFIRMED
- Both FOUND, headings "How the context window works" and "Context window overflow behavior" are real. Extra nuance (not an error): on Claude 4.5 and newer, input plus max_tokens over the window is accepted and stops with `model_context_window_exceeded`; the claim says only "input alone", which is correct.

### indirect-injection: CONFIRMED WITH CHANGES
- All 4 FOUND in the abstract (arXiv v2 5 May 2023, v1 23 Feb 2023).
- Text says Greshake "show ... because such applications blur the line". The abstract says "We argue that LLM-Integrated Applications blur the line between data and instructions" and "We show how processing retrieved prompts can act as arbitrary code execution, manipulate the application's functionality, and control how and if other APIs are called." Replacement: "Greshake et al. (2023) argue that LLM-integrated applications blur the line between data and instructions, and show how instructions planted in data likely to be retrieved can then act like arbitrary code execution and control whether and how other APIs are called."
- Independent: OWASP LLM01 describes indirect injection ("LLM accepts input from external sources, such as websites or files"): agrees.
- Technical note is honest (mechanism only).

### injection-no-foolproof: CONFIRMED WITH CHANGES
- All 3 FOUND. Excerpt 1 locator "Description" is wrong: the sentence is under "Prevention and Mitigation Strategies" (OWASP wording: "Given the stochastic influence at the heart of the way models work, it is unclear if there are fool-proof methods of prevention"). Excerpt 2 is in the Description. Third excerpt (external sources) is not used by the text; fine as support for the indirect form.
- "2025 Top 10" correct (page title LLM01:2025).
- The lesson turns "unclear if there are fool-proof methods" into "Nobody knows a foolproof way to stop that" in lesson.yaml challenge `injected-refund.explanation` and explain.observe.misconfigured. That is stronger than OWASP. Replace with "OWASP says it is unclear whether any fool-proof prevention exists."

### owasp-excessive-agency: CONFIRMED
- All 3 FOUND, under "Prevention and Mitigation Strategies" (items 1, 2 and 6 "Require user approval"). LLM06:2025 correct. Technical note matches the test.

### mcp-tools-primitive: CONFIRMED
- All 4 FOUND (bold/backtick markup only). Sections "Tools", "Listing Tools", "Calling Tools", "Data Types > Tool" exist. Text adds "a name, a description": both are in the same Tool list. Spec 2025-06-18 correct (a newer version may exist, as the register says).

### mcp-human-in-loop: CONFIRMED
- FOUND (page: "there **SHOULD** always be a human in the loop with the ability to deny tool invocations", in a warning box under User Interaction Model, which also says the protocol itself does not mandate any specific user interaction model) and "Clients SHOULD: Prompt for user confirmation on sensitive operations". Text keeps SHOULD. Independent: OWASP LLM06 item 6 agrees in spirit (recommendation, not a protocol rule).

---

## Part 3: other-provider comparison for the Anthropic/OpenAI/Gemini behaviour claims

| Behaviour | Anthropic | OpenAI | Gemini |
|---|---|---|---|
| Tool definition fields | name, description, input_schema (JSON Schema) | name, description, parameters (JSON schema), strict | name, description, parameters (OpenAPI schema subset) |
| Model only asks, app runs (client tools) | yes; Anthropic also runs server tools | yes; OpenAI also runs built-in tools | yes ("your responsibility"); built-in tools exist |
| Result linked to call | tool_use_id on tool_result | call_id | call_id on functionresult |
| tool_choice | auto, any, tool, none; any/tool rejected on several current models | auto, required, forced function, allowed_tools, none | AUTO, ANY, NONE, VALIDATED, allowed tools |
| Parallel calls | multiple tool_use blocks in one reply | parallel_tool_calls option | parallel and compositional calls |
| Loop signal | stop_reason tool_use | tool calls in output (Agents SDK handles it) | function-call step in the output |
| Server-held history | no (stateless request) | previous_response_id / conversation | previous_interaction_id |

Conflicts and caveats found: (1) Gemini is OpenAPI-schema, not JSON Schema; (2) forced tool use unsupported on some Anthropic models; (3) OpenAI "required" means one or more; (4) provider-run tools exist at all three, not only Anthropic; (5) Gemini and OpenAI also link results by call_id and can hold history server-side; (6) prompt caching changes the cost of re-sent history; (7) MCP separates protocol errors from isError errors.

---

## Part 4: implementation vs lesson text

Verified true (by running the code or reading it): default run order and 5 tool calls; step 2 `get_order("1001")` rejected with error "'order_id' must match ^A\d{4}$ (for example A1001), got '1001'"; retry with A1001 at step 3 (so explain.observe "Link it to call 3" is right); Return preset holds at needs_approval after 5 steps, 6 steps if approved; A1001 delivered 2026-10-05 = 16 days, A1002 2026-09-01 = 50 days, A1003 = 9 days (custom-built), A1004 shipped; fixed date 2026-10-21; 30-day window and "5 business days" are in the Lesson 01 "Returns and refunds" article; Too late preset: 3 tool calls then answer "delivered 50 days ago ... within 30 days"; Custom preset answers "custom-built bikes cannot be returned" (corpus text says so); Status preset 1 tool call, 2 steps; Policy preset 1 search, 2 steps; vague descriptions give every tool score 0.0 so the first tool is always picked; vague + no limit hits `safety_cap` at exactly 30 steps and re-reads far more tokens; tokens per step strictly increase (1475, 1955, 2203, 2526, 2799 for the default run); poisoned page with approval off produces an unapproved A1001 refund of 2899 CAD, approval on or refund tool removed produces none; all 3 challenges fail when broken and pass with the fix (test). Stage dependency order in the lesson `reconstruction` matches STAGE_DEPENDENCIES; explain.yaml `claims` equal the component `claims` for all 8 stages; every tour and challenge claim is among the lesson claims.

Mismatches and risks (all minor unless marked):

1. goal.breaks_if_removed "it takes no step at all" and ablation.py docstring "no step is taken": the run records one empty step (`stats.steps == 1`, status `no_goal`). Say "takes no action" or "does nothing".
2. data-flow visual description: "dashed lines carry tool calls and tool lists". The execute to observe link ("raw output") is flow `vector`, which the frontend draws dashed (Links3D STYLE), so a tool output is drawn dashed. Either change the link to `document` (solid, messages) or reword to "dashed lines carry tool calls, tool lists and tool output".
3. vague-tools brief: "Every tool is described as 'gets information' or 'does an action'". The third description is "Works something out." (days_between). Say "almost nothing".
4. decide.why (explain): "This is the only step that needs a model. Everything else in the loop is ordinary code." Uncited and false in general (guardrail models, summarisation/compaction). Say "In this loop, this is the only step that needs a model."
5. Stand-in realism: policy.py always obeys injected text; explain says "this stand-in follows it", which is honest. The lesson's claim about real models rests only on Greshake/OWASP. OK.
6. validate component says "against the tool's schema": it is a small subset validator (tools.py comment says so). Acceptable, optionally say "a simple version of JSON Schema".
7. Refund realism: `issue_refund` only appends to a per-run ledger (docstring says so) but neither corpus_note nor explain.execute says money does not move. Add "(the refund only writes a line in this run's list)".
8. visuals.experiment says "the token counts really run": the counts use Lesson 02's teaching tokenizer (explain.context.learn_more and pipeline TOKEN_LABEL say so). Add "with a teaching tokenizer" to the visual description.
9. stop component and explain.stop list two exits; the code has a third, `needs_approval` (loop pauses for a person). Not wrong, but a learner on the Return preset sees a stopped run that is neither answer nor step limit; one extra phrase would help.
10. Technical notes: agent-workflow-vs-agent overstated (see above); tool-result-linked test is a subset check; tool-errors-are-results test mostly exercises a validation error; tools-run-in-application note cites the ablation test not tagged to the claim. Other technical notes (agent-loop, validate, stopping, context-resent, tool-tokens-billed, injection, excessive-agency, mcp-human-in-loop) are accurate about what the passing tests prove.
11. explain.context text "The model keeps nothing between steps" and stop.why "every extra step costs more than the one before": true in this experiment (tokens strictly grow) and for a plain stateless API; add the caching/server-state caveat or scope to "in this loop".

## Part 5: honesty labels

- The stand-in is never presented as a real model: summary, decide.detail, visuals `decider` (kind `simulation`, "It is not a language model"), corpus_note, the vague-tools explanation, explain.decide.misconfigured, and the API payload (`model.kind: stand_in`, NOTE) all say so. No sentence found that claims real-model behaviour as measured.
- Visual kinds: ablation `real_execution` (correct: the real loop runs), experiment `real_execution` (correct, with the tokenizer wording fix above), exploded-view and data-flow `conceptual` (correct), decider `simulation` (correct).
- Minor wording risk: challenge brief "The agent keeps picking the wrong one" and the Return preset "the agent read the error and fix it" describe the stand-in's regex behaviour as the agent's reading; acceptable in context but the preset notes do not repeat the simulation label.

## Part 6: explain.yaml uncited factual assertions

Facts restating cited claims are fine. Uncited or stronger-than-cited factual statements:
- goal.learn_more: "Many real products are a workflow with one model call inside, and that is often the better choice." Not in any cited excerpt (Anthropic's "when to use agents" section recommends simple solutions first but does not say this). Cite or remove.
- tools.learn_more: "Tools are described the same way across providers" (see tool-definition).
- decide.why: "the only step that needs a model" (see above).
- execute.learn_more: "Anthropic also offers server tools" implies uniqueness (see tools-run-in-application).
- observe.learn_more: "Each provider links a result to its call" followed by two named providers (see tool-result-linked); "Nobody knows a foolproof way" in observe.misconfigured (see injection-no-foolproof).
- validate.learn_more: "the application should still check what it receives" is advice, supported in spirit by MCP "Servers MUST validate all tool inputs" but not stated about OpenAI strict mode.
- context.why / context.learn_more: "The model keeps nothing between steps"; "billed as input tokens" without caching caveat.
- stop.why: "every extra step costs more than the one before" (true in the experiment only).
- Generic opinion lines in misconfigured (e.g. "A real model can pick the wrong tool, write bad arguments or answer too early") are not cited; low risk, but they are claims about real models.

## Excerpts not found

None. Excerpts found with formatting differences only: "it's" curly apostrophe (stopping-conditions); markdown links or bold around the words in tool-definition (Anthropic and OpenAI), agent-workflow-vs-agent, mcp-tools-primitive, mcp-human-in-loop, tool-errors-are-results; OpenAI "Execute code on the application side..." is a list item with no final period.

Locators that do not name a real section: agent-workflow-vs-agent (all three: "Workflows and agents", real: "What are agents?"); tool-descriptions-matter excerpt 3 ("Prompt engineering your tools", real: "Summary"); tool-result-linked OpenAI ("The function calling flow (call_id)", real: "Tool call outputs"); sdk-max-turns excerpt 3 ("Runner options", real: "The agent loop"); injection-no-foolproof excerpt 1 ("Description", real: "Prevention and Mitigation Strategies"); tool-definition Anthropic ("Specifying client tools (input_schema)": heading is "Specifying client tools", acceptable); agent-loop is fine.
