# Beginner review: Lesson 05, Tool-using agents (plain words voice)

Reviewed: `_source/agents.json`, against `content/lessons/agents/{lesson,explain,teaching}.yaml` and `backend/app/experiments/agent/{policy,pipeline,tools,ablation}.py`. I also ran the backend loop to check the step counts, token numbers and final answers quoted in the text.

## Summary

The lesson's main idea gets through: the AI only asks, the program checks and does the work, the result goes back in, and the whole pile is read again each time. The worked example (the order number "1001" being rejected, then "A1001" accepted) is the best teaching device in the lesson. The honesty about the stand-in rule is also good.

The accuracy is mostly sound. Every step count I checked is right (5 steps, then 6 after approval; 4, 2 and 2 for the other presets), and so are 16 days, 50 days, and the token figures (1,475 at step 1, 2,799 at step 5, 10,958 across five steps). Nothing I found is flatly false. Several sentences drop a caveat or sound stronger than their source. The worst is the Policy preset note, which leaves out "after the warehouse inspects the bike".

What holds the lesson back for a true beginner is naming. Four things each carry two or three names, or one name with two meanings:
- "request" means three different things.
- "assistant", "agent", "model", "AI model" and "language model" are used for overlapping things.
- "step" means both one trip round the loop and one labelled part of the trip.
- The pile of notes is called the case file, the conversation, the context, "what the model reads", and sometimes includes the tool list and sometimes does not.

Fixing those four would remove most of the confusion. There are also several words used before they are explained: "stand-in", "the model", "the instructions", "plain loop", "tokenizer".

Counts: 0 WRONG, 11 MISLEADING, 23 CONFUSING.

Locations use `components[i]` in stage order: 0 goal, 1 tools, 2 decide, 3 validate, 4 execute, 5 observe, 6 context, 7 stop.

---

## Strengths to keep

- The restaurant menu analogy for the tool list ("You order from the descriptions, without seeing the kitchen", components[1].explain.analogy). It works, and it carries the point that the model never sees the code.
- The clerk who checks the form but "does not judge whether the request is a good idea" (components[3].explain.analogy, big_picture mapping). This keeps the real limit of checking.
- Handing the next shift "the entire case file every time, instead of a summary" (components[6].explain.analogy). It makes the growing reading cost easy to see.
- "A note slipped back across the desk" (components[5].explain.analogy).
- The "1001 versus A1001" thread runs through the lesson. It is concrete, and the rule "an A followed by four digits" is easy to follow.
- "Who actually runs a tool, the model or the program?" and its answer. It is clear and includes the honest bracket "(Some companies also offer tools that they run for you.)".
- The repeated honesty about the stand-in: "a simple match, not understanding", "so it shows the loop, not how a real model behaves", and the corpus_note saying no money moves and the shop is made up.
- "A step limit does not make the assistant right. It only stops the damage." and "a safety net, not a fix" (stop.misconfigured, challenge 1).
- "pretend list" instead of "ledger" (components[1].explain.thread).
- The quick presets, each with its step count ("Only two steps... Not every request needs the whole loop").
- The tour is short and in the right order. The tab descriptions ("The orange label is added by this site...") are clear.
- Challenge 3 ends on what you can do (limit the tools, add a person) rather than leaving the security point hopeless.

---

## Findings

### Names and meanings (job A4, and the biggest source of confusion)

**F1. CONFUSING. "request" has three meanings.**
- Quotes:
  - components[0].label "The request" (the customer's message)
  - components[3].explain.what "The program checks the request against the tool's rules before running it." (the model's ask)
  - components[1].explain.happens[1] "The list is added to every request." (a technical send to the AI)
  - components[1].explain.misconfigured "...also makes every request longer."
  - components[6].explain.misconfigured "...until a request no longer fits."
  - components[6].explain.example.steps[0] "The request + the tools + 3 requests + 3 results" (a customer message plus tool asks, in one line)
- Why: a beginner cannot tell which request is meant. The term "Tool call", defined in components[2].explain.terms, is then never used in the plain text.
- Replacements:
  - Call the customer's note "the customer's message". Keep "request" only for what the model asks for, and always say "tool request".
  - components[1].explain.happens[1]: "The list is shown to the model again at every step."
  - components[1].explain.misconfigured (last sentence): "Too many tools, or too much detail, also makes every step longer for the model to read."
  - components[3].explain.what: "The program checks the model's tool request against the tool's rules before running it."
  - components[6].explain.example.steps[0]: "The customer's message + the tools + 3 tool requests + 3 results"

**F2. CONFUSING. "agent", "assistant", "model", "AI model" and "language model" are never tied together.**
- Quotes:
  - components[0].explain.story "An agent starts with a request."
  - components[0].explain.why in the same stage "An assistant needs something to work towards."
  - components[1].explain.story "The assistant can only do what its tools allow... The model never sees the code behind a tool."
  - experiment.presets "...then the agent read the error and fix it." (Return note), "The agent has to search the policy..." (Too late note)
  - components[2].explain.terms defines "Language model" but the text never uses that phrase.
- Why: a learner will wonder whether the assistant and the model are two things. The preset notes revert to "agent" even though the stages say "assistant".
- Replacement: add once, early (in the goal stage story): "In this lesson the **assistant** is the whole system: an AI model that decides, plus a program that does the work. When we mean only the AI part, we say **the model**." Then use "assistant" in the preset notes.

**F3. CONFUSING. "step" means two things.**
- Quotes:
  - components[7].explain.what "A step limit is a second way out." (one trip round the loop)
  - components[3].explain.happens[2] "Send requests that pass on to the next step." (the next labelled part)
  - components[2].explain.why "this is the only step that needs an AI model." (a labelled part)
  - experiment.presets, Return note: "Watch the Check step reject it" (a labelled part)
  - experiment.guide.presets.Return.notice "Five steps are shown: ..." (trips)
- Why: "8 steps" and "the Check step" are different kinds of thing. The learner will try to count the lesson's eight labelled parts against the step limit.
- Replacement: use "part" for the eight labelled boxes and "round" or "step" only for one trip. For example, components[3].explain.happens[2] becomes "Send requests that pass on to the part that does the work." And Return note becomes "Watch the Check the form part reject it."

**F4. CONFUSING. The pile of notes has four names, and the contents change between places.**
- Quotes:
  - components[6].label "Case file"
  - components[6].explain.story "This is the context." and terms "Context: Everything the model is sent to read at a step: the instructions, the tools and the conversation so far."
  - components[6].explain.what "The whole conversation so far: the instructions, the tool list, every request and every result."
  - experiment.labels "What the model reads" (a tab)
- Why: "conversation" in the Case file definition includes the instructions and the tool list, but the Context definition lists them next to the conversation. A learner pictures a conversation as customer and assistant chat, not as a pile with a tool list in it.
- Replacement:
  - components[6].explain.what: "The case file: everything the model is shown at one step. That is the standing instructions, the tool list, the customer's message, every tool request so far and every result."
  - components[6].explain.story: "...This whole pile is also called the context."
  - Use "case file" everywhere else and drop "conversation" where it means the whole pile (components[0].detail, components[5], connections, tabs).

**F5. CONFUSING. Two or three names for the same limit and for the same controls.**
- Quotes:
  - components[7].explain.misconfigured "this experiment's own hard limit of 30 steps"
  - experiment.guide.ideas[0].see "the experiment's own safety limit of 30 steps"
  - experiment.labels "Limit on number of steps" and the text "step limit"
  - experiment.labels "Detailed": "Clear" (the control reads "Clear") against challenges[1].explanation "detailed descriptions" and the text "Vague"/"detailed"
  - ui.eyebrow "REQUEST → DECIDE → ACT → RESULT → REPEAT" ("ACT" is never a stage name; the stage is "Do the work")
  - experiment.presets Return note "the Check step" against the stage name "Check the form"
- Why: the learner sees "safety limit", "hard limit" and "step limit" and wonders whether there are three limits (there are two: the one you set, and a fixed one that cuts off a stuck loop).
- Replacement:
  - "the one you set is the step limit. There is also a fixed limit of 30 steps that this experiment uses to stop a loop that would never end."
  - Use one name each time. Use "clear" in the text for "Clear" descriptions.
  - Make the eyebrow use the stage names.

### Words not explained when first met (job A1)

**F6. CONFUSING. "the model" and "tool" are used before they are introduced.**
- Quotes:
  - components[1].explain.why "The model can only use what it is told about." (first stage to use "the model" on its own)
  - Earlier uses of "tools": summary "Run a real loop with real tools", objectives[0] "the tool list", components[0].explain.check.answer "choosing tools"
  - The definitions arrive later: "Tool" in components[1].explain.terms and "Language model" in components[2].explain.terms.
- Why: the learner meets the words two stages before they are defined.
- Replacement:
  - In components[0].explain.check.answer: "It can take several steps, using small ready-made actions called tools, and uses what each one sends back, in a loop, until the job is done."
  - Add in components[0] story: "Here, **the model** means the AI program that writes the text. It decides what to do next."

**F7. CONFUSING. "stand-in" is used before it is explained.**
- Quotes:
  - summary "(the decisions come from a clearly labelled stand-in)"
  - components[0].explain.misconfigured "this lesson's stand-in rule only recognises a few kinds of request."
  - components[1].explain.story "The stand-in here compares descriptions only."
- Why: "stand-in" for what? The meaning (a simple rule pretending to be the AI model) only appears in components[2].explain.happens[2] and the big picture, which come later.
- Replacement: summary: "...(the decisions come from a simple rule that pretends to be the AI model, and it is labelled so)." And at first use: "this lesson's stand-in rule (a simple rule that plays the part of the AI model)..."

**F8. CONFUSING. "the instructions" in the case file are never introduced.**
- Quotes:
  - components[6].detail "the instructions, the tool list, every request and every result"
  - components[6].explain.what "The whole conversation so far: the instructions, the tool list..."
  - components[6].explain.terms "Context: ...the instructions, the tools..."
- Why: nothing in the lesson tells the learner that the model is also given standing instructions (in the code, "You are Ridgeline Bikes' support agent. Answer the customer using the tools. Use only what the tools return.").
- Replacement: components[6].explain.story, first sentence: "At every step the model is also given its standing orders, such as 'answer the customer using the tools'."

**F9. CONFUSING. "plain loop" has nothing to contrast with.**
- Quotes: components[6].detail "In a plain loop, each step sends the whole conversation...", components[6].explain.why "In a plain loop the model keeps nothing between steps.", tour[6].body.
- Why: "plain" compared to what? The original said "plain API loop", and a beginner gets no hint of the other kind (where a service keeps the history for you).
- Replacement: "In a basic loop like this one, the model keeps nothing between steps. (Some services store the history for you.)"

**F10. CONFUSING. "tokenizer" is never explained.**
- Quotes: components[6].explain.thread "counted with this site's small teaching tokenizer", experiment.guide.ideas[3].see "counted with this site's small teaching tokenizer".
- Why: "token" is defined, "tokenizer" is not. "A token is a small piece of text" appears only after the number has been quoted.
- Replacement: "...counted with this site's simple way of cutting text into small pieces called tokens, so a real model's counts would be different."

**F11. CONFUSING. Code-style names in examples.**
- Quotes:
  - components[1].explain.example.input "search_help_centre, get_order, days_between, issue_refund"
  - components[4].explain.example.input "get_order(order_id=A1001)" and output "{item, price, status, delivered}"
  - components[5].explain.example.input "get_order → A1001 found"
- Why: underscores and brackets are what a beginner sees as "computer stuff". These are the first things they read in the example box.
- Replacements:
  - components[1].explain.example.input: "Search the help centre, look up an order, count days between two dates, issue a refund"
  - components[4].explain.example.input: "Look up order A1001"
  - components[4].explain.example.output: "The order's item, price, status and delivery date (an illustration)"
  - components[5].explain.example.input: "The order lookup found order A1001"

**F12. CONFUSING. A few small unexplained words.**
- "ordinary code" (components[2].explain.why, components[4].explain.happens[1]): "ordinary code" is vague. Suggest "plain instructions the program follows".
- "wrapped in a result message" (components[5].explain.happens[0]): suggest "put into a result message".
- "raw output" (connections[4].payload and components[4].outputs): suggest "what the tool sent back".
- "custom-built flag" (guide.presets.Custom.notice): "flag" here means a yes/no marker. Suggest "the order's 'custom-built' marker".
- "2,899 CAD" with no explanation (components[5].explain.thread): suggest "2,899 Canadian dollars".
- "Tools that change things, such as a refund, are marked" (components[1].explain.happens[2]): marked by whom? The tools tab says the orange label is added by this site for the reader. Suggest "On this site, tools that change things, such as a refund, carry an orange label so you can spot them."
- "server" (ui.challenges_intro "The server runs your settings again"): suggest "The site runs your settings again and checks the result."

### Sentences that need a second read (job A2)

**F13. CONFUSING. "A model's request is not a guarantee."**
- Quotes: components[3].explain.why "A model's request is not a guarantee.", components[3].explain.story "A model's request is not a guarantee.", components[3].explain.goes_to "Do the work, if the request is fine."
- Why: a guarantee of what? And "fine" can read as "approved", which contradicts the clerk analogy.
- Replacements:
  - why: "A model can write a request that is badly put together, so the program cannot assume it is correct."
  - goes_to: "Do the work, if the request is in the right shape. Back to the model as an error, if not."

**F14. CONFUSING. "points at the request it answers".**
- Quotes: components[5].detail "goes back to the model as a message that points at the request it answers. Whatever a tool returns is just information, but the model reads it like everything else.", components[5].explain.example.steps[1] "Link it to request 3".
- Why: "points at" and "request 3" assume the learner knows requests are numbered and matched to results. The last sentence hints at a danger that is not named, so it needs a second read.
- Replacement: "The output, or the error, goes back to the model as a message that says which of its tool requests it is the answer to. A tool's output is only information, but the model reads it the same way it reads everything else, which can be a risk (see below)." And for the example: "Tag it as the answer to tool request 3."

**F15. CONFUSING. Long chain in the Return preset note.**
- Quote: experiment.guide.presets.Return.notice "Five steps are shown: the assistant first searches the help centre for the policy, then writes the order as "1001" and the check rejects it, tries again with "A1001", counts 16 days, and asks for the refund, which waits for you."
- Why: the subject changes mid-sentence (who "tries again"?), and "counts 16 days" can read as counting for 16 days. The key moment (the rejection) is buried.
- Replacement: "Five steps are shown. 1: it searches the help centre for the policy. 2: it writes the order as "1001" and the check rejects it. 3: it tries again with "A1001". 4: it works out that 16 days have passed since delivery. 5: it asks for the refund, which waits for you. After you approve, it takes a sixth step and the assistant answers."

**F16. CONFUSING. Long opening sentences.**
- Quote: big_picture.story "An agent is an AI model that can ask for actions to be taken. Instead of answering straight away, it works in a loop: it decides what to do next, asks for a tool, your program runs that tool, the result goes back to the model, and the model decides again, until it has an answer."
- Why: five actions in one sentence; the subject changes from the model to the program and back.
- Replacement: "An assistant does not answer straight away. It goes round a loop. First the model decides what to do next and asks for a tool. Then the program runs that tool. The result goes back to the model, and the model decides again. This repeats until it has an answer."
- Other long ones:
  - components[1].explain.story third sentence "The model never sees the code behind a tool, only its name, description and rules, and the description is the most important part for choosing the right tool." Split at "and".
  - components[2].explain.story second sentence "Then, in this lesson, it either asks for one tool (with the details it needs) or gives the final answer."
  - big_picture.analogy.breaks.

**F17. CONFUSING. The bars are mentioned before anyone has seen them.**
- Quote: components[2].explain.story "...and the bars count the words each tool's description shares with what it needs: a simple match, not understanding."
- Why: "the bars" and "what it needs" have no referent yet. Also, the bars show a share (the code divides shared words by the words it wants), not a count.
- Replacement: "In the step-by-step view you will see a small bar beside each tool. Each bar shows how many of the words the assistant wants appear in that tool's description. That is a simple word match, not understanding."

**F18. CONFUSING. Five steps and six steps in nearby text.**
- Quotes: components[6].explain.thread "...by step 5 it reads 2,799, about 11,000 across the five steps." and components[7].explain.thread "That took 6 steps in all."
- Why: the learner sees "five" and "six" for the same request. The first figure is for the run that is paused before the refund is approved.
- Replacement: components[6].explain.thread: "...before you approve the refund, step 1 reads about 1,475 tokens and step 5 reads 2,799, about 11,000 across those five steps."

**F19. CONFUSING. Case-file misconfigured sentence.**
- Quote: components[6].explain.misconfigured "Take the memory away in the experiment and the assistant repeats itself. Keep too much and every step gets slower and costs more, until a request no longer fits."
- Why: "Take the memory away in the experiment" does not match any control; the action is in the "Real run, one part removed" view. "Keep too much" of what? "a request no longer fits" is a technical limit with no setup.
- Replacement: "In the 'one part removed' view, take away the case file and the assistant repeats itself. If the case file is kept too long, every step costs more to read, and in the end the pile can get too big for the model to take in at once."

**F20. CONFUSING. Tools "connection" sentence.**
- Quote: connections[1].explain "It is meant to choose only from what it has been shown, and the program should refuse any other name."
- Why: "it" could be the list or the model, and "refuse any other name" has no object.
- Replacement: "The model is meant to ask only for tools on this list, and the program should refuse a request for any tool that is not on it."

**F21. CONFUSING. Who is "you" in "tools you define yourself".**
- Quotes: components[4].explain.story "For tools you define yourself, the model only asks. Your program runs the tool", components[4].explain.check.answer "For tools you define yourself, the program.", components[4].subtitle "Your program does the work", big_picture.story "your program".
- Why: the learner is not building anything, so "your program" is odd. Other places say "the program".
- Replacement: "For tools the shop's own program provides, the model only asks and the program does the work. (Some companies also offer tools they run for you.)" Use "the program" everywhere.

### Analogies that mislead, and gaps (job A3)

**F22. MISLEADING. The execute analogy reverses who is in charge.**
- Quote: components[4].explain.analogy "A manager who carries out what the worker asks for, and who can say no."
- Why: managers do not carry out their workers' requests, and the big picture calls the same part "the back office". Two analogies for one stage. Also "can say no" gets muddled with the check stage.
- Replacement: "The back office: it does the job the helpdesk worker asks for. A person in the back office can also hold a risky job until someone senior says yes."

**F23. MISLEADING. The Stop analogy covers only half of Stop.**
- Quote: components[7].explain.analogy "A timer on a task, so a stuck worker gets stopped and asked what is wrong."
- Why: Stop is also the normal ending when the model answers. A timer only matches the step limit. The big picture mapping covers both.
- Replacement: "The worker hands over the answer when it is ready. A timer on the task stops a stuck worker so someone can ask what is wrong."

**F24. MISLEADING. "agent" defined as just an AI model.**
- Quotes: components[0].explain.terms "Agent: An AI model that can ask for actions to be taken, and works in a loop", big_picture.story "An agent is an AI model that can ask for actions to be taken."
- Why: later text says the program runs the tools, checks the requests and keeps the loop going. The AI model alone does none of those.
- Replacement: "Agent: an AI model together with a program that lets it ask for actions and keeps going round a loop until the job is done."

### Marketing, vagueness, talking down (job A5)

**F25. CONFUSING. "A well-known security group".**
- Quotes: components[5].explain.misconfigured, challenges[2].explanation.
- Why: a vague appeal to authority, and an unnamed source cannot be checked. The source (OWASP) is named in explain.yaml.
- Replacement: "OWASP, a non-profit group that publishes security guidance for AI software, says it is not clear whether any method can completely prevent this."

**F26. CONFUSING. "That is powerful but risky".**
- Quote: components[5].explain.story "That is powerful but risky: if a result contains hidden instructions, the model may treat them as commands."
- Why: "powerful" reads like a sales word; the real point is that it is useful because the model can use what it finds.
- Replacement: "That is useful, because the model can use what the tool found. It is also risky: if a result contains hidden instructions, the model may treat them as commands."

I found nothing that talks down to the reader.

---

### Accuracy (job B)

**F27. MISLEADING. Policy preset drops the caveat on the 5-day refund.**
- Quote: experiment.guide.presets.Policy.notice "...an answer that says refunds go to the original payment method within 5 business days."
- Why: the help-centre text, and the answer the code gives, say "within 5 business days after the warehouse inspects the bike". Leaving that out makes it sound like 5 days from asking. (teaching.yaml has the same omission.)
- Replacement: "Two steps: one help-centre search, then an answer that says refunds go to the original payment method within 5 business days after the warehouse inspects the bike."

**F28. MISLEADING. Real token counts "would be lower".**
- Quotes: components[6].explain.thread "so a real model's counts would be lower", experiment.guide.ideas[3].see "(a real model's counts would be lower...".
- Why: the code label (pipeline.py TOKEN_LABEL) and explain.yaml say only "real counts differ". No test or claim checks the direction.
- Replacement: "...so a real model's counts would be different, but each step would still read more than the one before."

**F29. MISLEADING. "Cost grows" with no caveat that services can lower it.**
- Quotes: components[6].explain.check.answer "...the whole thing is read again at every step.", components[7].explain.why "in this loop every extra step costs more than the one before", tour[6].body "so the cost grows with every step."
- Why: explain.yaml adds that some services store the history and charge less for a repeated start. The plain text qualifies it with "in a plain loop" (see F9) but never says what the exception is. "Gets slower" in components[6].explain.misconfigured is also not measured or verified anywhere (the experiment counts tokens, not time).
- Replacement: add one sentence to components[6].explain.story: "Some services can store the start of the pile and charge less to read it again, but the model still has to take in all of it each time." And drop "slower", or say "can take longer".

**F30. MISLEADING. "Anything that changes the real world" is stronger than the source.**
- Quote: components[4].explain.misconfigured "Anything that changes the real world is a place for a person to say yes first".
- Why: OWASP and MCP say to require a person to approve high-impact actions. "Anything" would mean approval for every small change.
- Replacement: "Anything risky that changes the real world, such as moving money, is a place for a person to say yes first."

**F31. MISLEADING. "a real AI model would read the policy text".**
- Quote: experiment.guide.presets.Custom.notice "A real AI model would read the policy text."
- Why: stated as certain. A real model may read the policy text, but this is not checked, and the original said it more cautiously.
- Replacement: "A real AI model could read the policy text as well."

**F32. MISLEADING. The "most important part" is stated as fact.**
- Quotes: components[1].explain.story "the description is the most important part for choosing the right tool", components[1].explain.check.answer.
- Why: in the sources this is Anthropic's advice ("by far the most important factor in tool performance"). The challenge explanation correctly attributes it; the stage text does not. Real models also read the tool name and the rules.
- Replacement: "Anthropic, a company that builds AI models, advises that clear descriptions matter most for good tool choices."

**F33. MISLEADING. The vague-tools explanation describes the stand-in as if it were the assistant.**
- Quote: challenges[1].explanation "The assistant chooses a tool by comparing what it needs with the tool descriptions. When every description says almost nothing, every tool scores the same and it just takes the first one."
- Why: the first two sentences describe this site's simple word-match rule, not how a real model chooses. The caveat comes at the end of the paragraph.
- Replacement: "The stand-in rule chooses a tool by counting how many of its wanted words appear in each description. When every description says almost nothing, every tool scores zero and it just takes the first one. A real model works differently, but Anthropic also calls detailed descriptions by far the most important factor in how well tools work."

**F34. MISLEADING (minor). "does not exist" is stronger than the actual reply.**
- Quotes: components[3].breaks_if_removed "...the assistant tells the customer their order does not exist.", components[3].explain.misconfigured same.
- Why: the code's reply is "I couldn't find an order called 1001." (The guide idea quotes it correctly.) The lesson's wrong-answer point is that the order does exist as A1001, so "couldn't find" is the more accurate phrase.
- Replacement: "...so the assistant tells the customer it could not find their order, even though the order exists."

---

## Counts

- WRONG: 0
- MISLEADING: 11 (F22, F23, F24, F27, F28, F29, F30, F31, F32, F33, F34)
- CONFUSING: 23 (F1 to F21, F25 and F26)

F12 groups several small words into one item.
