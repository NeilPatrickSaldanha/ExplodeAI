# Research brief: Lesson 05 · Tool-using agent, exploded

Pass 1 (primary sources) for a beginner lesson. Every claim must be citable: URL, access date
(2026-10-21), version or "last updated" date, and a short excerpt (≤ 30 words). Never fabricate;
mark anything that cannot be confirmed. Record provider-specific facts as provider-specific.

Output: notes in this folder, and a synthesis at `reports/Agents primary sources.md` in the same
format as `reports/Attention primary sources.md` (source register, claims table with
claim / source / locator / excerpt, conflicts, gaps).

## The lesson's machine (stages to research)

1. **What an agent is.** A model in a loop that calls tools; workflows vs agents (Anthropic,
   "Building effective agents", Dec 2024); ReAct (arXiv 2210.03629, note the version read);
   Toolformer (2302.04761); MRKL (2205.00445).
2. **Tool registry.** Tool definitions: name, description, JSON Schema input (Anthropic tool-use
   docs, OpenAI function calling, Gemini function calling). Why detailed descriptions matter.
3. **Decide.** Tool-use / function-call output blocks; stop_reason "tool_use"; tool_choice
   (auto / any / none / a specific tool); parallel tool calls.
4. **Validate arguments.** Models can produce invalid arguments; strict mode / structured
   outputs; the application must validate.
5. **Execute.** The application runs client tools, not the model; client vs server tools.
6. **Observation.** tool_result blocks, tool_use_id, is_error; results appended to the conversation.
7. **Context.** Each turn re-sends the history; tool results cost tokens; context-window limits.
8. **Stop.** The model ends its turn with a final answer; step limits as a guard (OpenAI Agents
   SDK max_turns, LangGraph recursion_limit); runaway loops and cost.
9. **Safety.** Indirect prompt injection through tool outputs (Greshake et al., 2302.12173);
   OWASP Top 10 for LLM Apps: prompt injection and excessive agency; human approval for tools
   with side effects; least privilege.
10. **Model Context Protocol.** Spec version and the tools primitive, as a standard way to expose tools.
