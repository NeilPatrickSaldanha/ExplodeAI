# Agents primary sources

Pass 1 synthesis for **Lesson 05 · Tool-using agents, exploded** (`content/lessons/agents/lesson.yaml`).
Researched 2026-10-22. Notes and raw outputs: `research_notes/Agents primary sources/`.

> Pass 1 gathers the evidence; it does not by itself make a claim true. Every source records the
> date it was read, and pages without a version or date say so.

## How it was done

- `deep-research` run 1 (stages 1 to 8): 11 findings, all verified by three-vote adversarial checks. 0 refuted.
- `deep-research` run 2 (context growth, safety, MCP): the first attempt hit a usage limit and returned nothing. The rerun returned 9 findings and refuted 1 (a Gemini claim, below).
- Direct page reads for what the runs left open: the OWASP LLM06 mitigations, the MCP tools specification (2025-06-18), and verbatim quotes for the Anthropic, OpenAI, Gemini and arXiv pages.
- Raw outputs: `pass1_run1_raw.json`, `pass1_run2_raw.json`. Brief: `brief.md`.

## Source register

| id | Source | Publisher | Version read | Accessed |
|---|---|---|---|---|
| `anthropic_building_agents` | [Building effective agents](https://www.anthropic.com/research/building-effective-agents) | Anthropic | 2024-12-19 | 2026-10-22 |
| `yao2022react` | [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) | arXiv / ICLR 2023 | arXiv v3 (10 Mar 2023, ICLR camera-ready) | 2026-10-22 |
| `schick2023toolformer` | [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761) | arXiv / NeurIPS 2023 | arXiv v1 (9 Feb 2023), the only version listed | 2026-10-22 |
| `karpas2022mrkl` | [MRKL Systems: A modular, neuro-symbolic architecture that combines lar](https://arxiv.org/abs/2205.00445) | arXiv | arXiv v1 (1 May 2022), the only version listed | 2026-10-22 |
| `greshake2023injection` | [Not what you've signed up for: Compromising Real-World LLM-Integrated ](https://arxiv.org/abs/2302.12173) | arXiv | arXiv v2 (5 May 2023); first posted v1 on 23 Feb 2023 | 2026-10-22 |
| `anthropic_tool_how` | [How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works) | Anthropic (Claude API docs) | live page at access date (no date shown) | 2026-10-22 |
| `anthropic_tool_define` | [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools) | Anthropic (Claude API docs) | live page at access date (no date shown) | 2026-10-22 |
| `anthropic_tool_overview` | [Tool use with Claude (overview, including pricing)](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) | Anthropic (Claude API docs) | live page at access date (no date shown); the old tool-use-pricing-and-tokens URL redirects here | 2026-10-22 |
| `anthropic_context_windows` | [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) | Anthropic (Claude API docs) | live page at access date (no date shown) | 2026-10-22 |
| `openai_function_calling` | [Function calling](https://developers.openai.com/api/docs/guides/function-calling) | OpenAI (API docs) | live page at access date (no date shown) | 2026-10-22 |
| `gemini_function_calling` | [Function calling with the Gemini API](https://ai.google.dev/gemini-api/docs/function-calling) | Google AI for Developers | live page at access date (no date shown) | 2026-10-22 |
| `openai_agents_running` | [Running agents (OpenAI Agents SDK for Python)](https://openai.github.io/openai-agents-python/running_agents/) | OpenAI | live page at access date (no version or date shown) | 2026-10-22 |
| `owasp_llm01` | [LLM01:2025 Prompt Injection (OWASP Top 10 for LLM Applications)](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | OWASP GenAI Security Project | 2025 list; page shows only a 2025 copyright | 2026-10-22 |
| `owasp_llm06` | [LLM06:2025 Excessive Agency (OWASP Top 10 for LLM Applications)](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) | OWASP GenAI Security Project | 2025 list; page shows only a 2025 copyright | 2026-10-22 |
| `mcp_tools_20250618` | [Tools (Model Context Protocol specification)](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) | Model Context Protocol | specification 2025-06-18 (read as this dated version; a newer version may exist) | 2026-10-22 |

## Claims and excerpts

Each excerpt is 30 words or fewer. (Pass 2 re-checked every one against the live page; see the verification report.)

| Claim | Source | Locator | Excerpt |
|---|---|---|---|
| `agent-workflow-vs-agent` | `anthropic_building_agents` | What are agents? | “Workflows are systems where LLMs and tools are orchestrated through predefined code paths.” |
|  | `anthropic_building_agents` | What are agents? | “Agents, on the other hand, are systems where LLMs dynamically direct their own processes and tool usage” |
|  | `anthropic_building_agents` | What are agents? | “At Anthropic, we categorize all these variations as agentic systems” |
| `agent-loop` | `anthropic_building_agents` | Agents | “They are typically just LLMs using tools based on environmental feedback in a loop.” |
|  | `anthropic_tool_how` | The agentic loop (client tools) | “every tool call is a round trip: the model asks, you execute, you report back, the model continues.” |
| `react-origin` | `yao2022react` | Abstract | “generate both reasoning traces and task-specific actions in an interleaved manner” |
|  | `yao2022react` | Abstract | “interface with external sources, such as knowledge bases or environments” |
| `toolformer-origin` | `schick2023toolformer` | Abstract | “a model trained to decide which APIs to call, when to call them, what arguments to pass” |
| `mrkl-origin` | `karpas2022mrkl` | Abstract | “we define a flexible architecture with multiple neural models, complemented by discrete knowledge and reasoning modules” |
| `tool-definition` | `anthropic_tool_define` | Specifying client tools (input_schema) | “A JSON Schema object defining the expected parameters for the tool.” |
|  | `anthropic_tool_define` | Specifying client tools (name) | “The name of the tool. Must match the regex ^[a-zA-Z0-9_-]{1,128}$.” |
|  | `openai_function_calling` | Defining functions (parameters) | “JSON schema defining the function's input arguments” |
|  | `gemini_function_calling` | Function declarations (name) | “Unique function name (use underscores or camelCase).” |
|  | `gemini_function_calling` | Function declarations (notes) | “only a subset of the OpenAPI schema is supported” |
|  | `gemini_function_calling` | Function declarations (description) | “Clear explanation of the function's purpose.” |
|  | `gemini_function_calling` | Function declarations (parameters) | “Input parameters the function expects.” |
| `tool-descriptions-matter` | `anthropic_tool_define` | Best practices for tool definitions | “Provide extremely detailed descriptions. This is by far the most important factor in tool performance.” |
|  | `anthropic_tool_define` | Best practices for tool definitions | “Aim for at least 3–4 sentences for each tool description, more if the tool is complex.” |
| `tool-choice` | `anthropic_tool_define` | Forcing tool use (tool_choice) | “auto allows Claude to determine whether to call any provided tools. This is the default value when tools are provided.” |
|  | `anthropic_tool_define` | Forcing tool use (tool_choice) | “any tells Claude that it must use one of the provided tools, but doesn't force a particular tool.” |
|  | `anthropic_tool_define` | Forcing tool use | “Not every model and setting supports forced tool use.” |
|  | `openai_function_calling` | Tool choice (auto) | “Call zero, one, or multiple functions.” |
|  | `openai_function_calling` | Tool choice (required) | “Call one or more functions.” |
|  | `openai_function_calling` | Tool choice (forced) | “Call exactly one specific function.” |
|  | `gemini_function_calling` | Function calling modes (ANY) | “Model is constrained to always predict a function call.” |
| `tools-run-in-application` | `anthropic_tool_how` | The tool-use contract | “The model never runs anything on its own.” |
|  | `gemini_function_calling` | How function calling works | “The model doesn't execute the function itself.” |
|  | `openai_function_calling` | The function calling flow | “Execute code on the application side with input from the tool call” |
|  | `anthropic_tool_how` | Server-executed tools | “Anthropic runs the code. You enable the tool in your request and the server handles everything else.” |
| `tool-result-linked` | `openai_function_calling` | Tool call outputs | “should contain a reference to a specific model tool call (referenced by call_id in the examples to come)” |
|  | `anthropic_tool_overview` | How tool use works (Python example) | “{"type": "tool_result", "tool_use_id": tool_use.id, "content": weather}” |
| `loop-stop-reason` | `anthropic_tool_how` | The agentic loop (client tools) | “Claude responds with stop_reason: "tool_use" and one or more tool_use blocks.” |
|  | `anthropic_tool_how` | The agentic loop (client tools) | “Repeat from step 2 while stop_reason is "tool_use".” |
|  | `anthropic_tool_how` | The agentic loop (client tools) | “The loop exits on any other stop reason ("end_turn", "max_tokens", "stop_sequence", or "refusal")” |
| `tool-errors-are-results` | `mcp_tools_20250618` | Error Handling | “Tool Execution Errors: Reported in tool results with isError: true” |
|  | `mcp_tools_20250618` | Error Handling | “Invalid input data” |
|  | `mcp_tools_20250618` | Error Handling | “Protocol Errors: Standard JSON-RPC errors for issues like:” |
| `validate-tool-inputs` | `mcp_tools_20250618` | Security Considerations (servers MUST) | “Validate all tool inputs” |
|  | `openai_function_calling` | Strict mode | “will ensure function calls reliably adhere to the function schema” |
| `stopping-conditions` | `anthropic_building_agents` | Agents | “it's also common to include stopping conditions (such as a maximum number of iterations) to maintain control.” |
| `agents-cost-errors` | `anthropic_building_agents` | Agents | “The autonomous nature of agents means higher costs, and the potential for compounding errors.” |
|  | `anthropic_building_agents` | Agents | “We recommend extensive testing in sandboxed environments, along with the appropriate guardrails.” |
| `sdk-max-turns` | `openai_agents_running` | The agent loop | “If the LLM produces tool calls, we run those tool calls, append the results, and re-run the loop.” |
|  | `openai_agents_running` | The agent loop | “If we exceed the max_turns passed, we raise a MaxTurnsExceeded exception.” |
|  | `openai_agents_running` | The agent loop | “Pass max_turns=None to disable this turn limit.” |
| `context-resent` | `anthropic_tool_how` | The agentic loop (client tools) | “Send a new request containing the original messages, the assistant's response, and a user message with the tool_result blocks.” |
|  | `anthropic_context_windows` | How the context window works | “Contains all previous conversation history plus the current user message” |
| `tool-tokens-billed` | `openai_function_calling` | Token usage | “callable function definitions count against the model's context limit and are billed as input tokens.” |
|  | `anthropic_tool_overview` | Pricing | “The total number of input tokens sent to the model (including in the tools parameter)” |
|  | `anthropic_tool_overview` | Pricing | “tool_result content blocks in API requests” |
| `context-window-limit` | `anthropic_context_windows` | How the context window works | “Everything in the request counts toward the context window: the system prompt, every message in messages (including tool results, images, and documents), and your tool definitions.” |
|  | `anthropic_context_windows` | Context window overflow behavior | “If the input alone already exceeds the model's context window, the API returns a 400 invalid_request_error” |
| `indirect-injection` | `greshake2023injection` | Abstract | “by strategically injecting prompts into data likely to be retrieved” |
|  | `greshake2023injection` | Abstract | “We argue that LLM-Integrated Applications blur the line between data and instructions.” |
|  | `greshake2023injection` | Abstract | “We show how processing retrieved prompts can act as arbitrary code execution” |
|  | `greshake2023injection` | Abstract | “control how and if other APIs are called” |
| `injection-no-foolproof` | `owasp_llm01` | Prevention and Mitigation Strategies | “it is unclear if there are fool-proof methods of prevention for prompt injection.” |
|  | `owasp_llm01` | Description | “research shows that they do not fully mitigate prompt injection vulnerabilities” |
|  | `owasp_llm01` | Description (indirect prompt injection) | “when an LLM accepts input from external sources, such as websites or files” |
| `owasp-excessive-agency` | `owasp_llm06` | Prevention and mitigation | “Limit the extensions that LLM agents are allowed to call to only the minimum necessary.” |
|  | `owasp_llm06` | Prevention and mitigation | “Limit the permissions that LLM extensions are granted to other systems to the minimum necessary” |
|  | `owasp_llm06` | Prevention and mitigation | “Utilise human-in-the-loop control to require a human to approve high-impact actions before they are taken.” |
| `mcp-tools-primitive` | `mcp_tools_20250618` | Tools | “allows servers to expose tools that can be invoked by language models.” |
|  | `mcp_tools_20250618` | Listing Tools | “To discover available tools, clients send a tools/list request.” |
|  | `mcp_tools_20250618` | Calling Tools | “To invoke a tool, clients send a tools/call request:” |
|  | `mcp_tools_20250618` | Data Types (Tool) | “inputSchema: JSON Schema defining expected parameters” |
| `mcp-human-in-loop` | `mcp_tools_20250618` | User Interaction Model | “there SHOULD always be a human in the loop with the ability to deny tool invocations.” |
|  | `mcp_tools_20250618` | Security Considerations (clients SHOULD) | “Prompt for user confirmation on sensitive operations” |

## Conflicts and caveats found

1. **Gemini and token billing (refuted).** A claim that Gemini counts tool definitions toward billed tokens was refuted 0 to 3 by the verifiers (the page does not say it). It is not in the lesson; the billed-token claim cites only OpenAI and Anthropic.
2. **Forced tool use is not universal.** Anthropic's define-tools page says `any` and `tool` return a 400 error on several current models and under manual extended thinking. The tool-choice claim says so. (Found in Pass 2.)
3. **Gemini's schema is not JSON Schema.** It documents a subset of the OpenAPI schema. The tool-definition claim says so. (Pass 2.)
4. **Prompt caching and server-held history.** Caching changes what a re-sent history costs, not whether it counts; OpenAI and Gemini can hold history on the server. The lesson scopes its context claims to a plain API loop. (Pass 2.)
5. **Prompt injection wording.** OWASP says it is "unclear" whether foolproof prevention exists. The lesson uses that wording, not a stronger one.
6. **MCP errors.** Unknown tools and bad arguments are JSON-RPC protocol errors; only failures while a tool runs use `isError`. The lesson says so.

## Gaps (not used in the lesson)

- **MCP "current" version.** Only specification 2025-06-18 was read. A newer version may exist, and the lesson names the version it cites.
- **Anthropic's `is_error` field.** Not confirmed from the page prose in Pass 1, so no claim uses it. ExplodeAI's `is_error` is its own name; the MCP claim cites `isError`.
- **Anthropic's "Advanced tool use" post** (tool definitions using tens of thousands of tokens). Anecdotal and promotional, so it is not cited.
- **Gemini tool-choice modes and parallel calls.** Read in Pass 2 but only partly quoted; the lesson cites one Gemini mode.
- **Dates.** The OpenAI, Gemini, Anthropic docs and OWASP pages show no last-updated date, so each source records "live page at access date".
- **Real-model behaviour.** Whether a real model follows hidden instructions, or picks the wrong tool when descriptions are vague, is not measured here. The lesson's stand-in shows the mechanism only and says so.
