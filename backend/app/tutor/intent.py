"""Small talk and follow-ups: what is the learner asking for, beyond a topic?

Rule-based and deterministic. A follow-up like "say that more simply" has no topic of its own, so
it is answered about the stage the conversation was last on.
"""

import re

OVERVIEW = re.compile(
    r"(\b(what|which|list|show|name|tell me)\b.{0,30}\b(lessons?|topics|chapters|modules|courses)\b|"
    r"\bwhat (can|do|will) (you|i|we)\b.{0,20}\b(teach|cover|know|help|learn)\b|"
    r"\bwhat('s| is) (this|explodeai|here)\b( (site|app|website|about|for))*|"
    r"\b(syllabus|curriculum|table of contents|where (do|should) i (start|begin))\b)",
    re.I,
)
LESSON_ABOUT = re.compile(r"\b(lesson|chapter)\s*(0?([1-4])|(one|two|three|four))\b", re.I)
HELP = re.compile(
    r"(how (do|can|should) i use|how does (this|the) (site|app|website|page) work|what are the (modes|tabs)|"
    r"what (is|does) (the )?(tour|explore|experiment|break (&|and) fix|rebuild)\b|help me (start|use)|"
    r"how do i (start|begin|get started))",
    re.I,
)
_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4}


def lesson_number(question: str) -> int | None:
    m = LESSON_ABOUT.search(question)
    if not m:
        return None
    return int(m.group(3)) if m.group(3) else _WORDS[m.group(4).lower()]


GREETING = re.compile(
    r"^\W*(hi|hello|hey|hiya|yo|howdy|good (morning|afternoon|evening)|sup)\b.{0,20}$", re.I
)
THANKS = re.compile(
    r"^\W*(thanks|thank you|thx|ty|cheers|great|awesome|nice|cool|got it|ok(ay)?|makes sense)\b.{0,25}$", re.I
)
SIMPLIFY = re.compile(
    r"(simpl|easier|easy words|plain (english|words|language)|eli5|like i'?m (5|five)|dumb it down|"
    r"(don'?t|do not|didn'?t|did not) (get|understand)|confus|lost me|too (hard|technical|complicated)|"
    r"in other words|rephrase|reword|break (it|that) down|explain (it|that) (again|better|differently))",
    re.I,
)
EXAMPLE = re.compile(r"\b(example|for instance|show me how|walk me through|demo)\b", re.I)
MORE = re.compile(
    r"^\W*(more|tell me more|go on|continue|and then|what else|anything else|elaborate|expand)\b", re.I
)
WHY_MATTERS = re.compile(
    r"\b(why does (it|that|this) matter|why (is|does) (it|that|this)|why do we need (it|this))\b", re.I
)
ANAPHORA = re.compile(r"\b(it|that|this|they|them|those|these|the same|there)\b", re.I)

GREETING_REPLY = (
    "Hi! I'm the ExplodeAI tutor. Ask me about anything in the four lessons, in your own words. "
    "I can explain a stage simply, give an example, or quiz you on the stage you have open."
)
THANKS_REPLY = "Glad it helped. Ask another question, or press “Quiz me” to test yourself on this stage."
HELP_REPLY = (
    "Click any part of the 3D machine, or any card in the stage bar, to see what it does. "
    "The five modes along the top: Explore (click around), Tour (a guided walk, with Play and Pause), "
    "Experiment (run the real code on your own input), "
    "Break & fix (repair something that is broken) and Rebuild (put the stages in order). "
    "The “How to use” button at the top of a lesson replays the guided tutorial."
)
NEEDS_TOPIC = (
    "Which part should I explain? Pick a stage or ask a question about it first, then ask me to simplify."
)


def classify(question: str) -> str | None:
    q = question.strip()
    if GREETING.match(q):
        return "greeting"
    if THANKS.match(q):
        return "thanks"
    if HELP.search(q):
        return "help"
    if (
        LESSON_ABOUT.search(q)
        and re.search(r"\b(about|cover|covers|teach|teaches|in|is|explain|summary|summar)", q, re.I)
        and len(q.split()) <= 12
    ):
        return "lesson_about"
    if OVERVIEW.search(q) and len(q.split()) <= 14:
        return "overview"
    if SIMPLIFY.search(q):
        return "simplify"
    if EXAMPLE.search(q) and len(q.split()) <= 8:
        return "example"
    if MORE.match(q):
        return "more"
    if WHY_MATTERS.search(q) and len(q.split()) <= 8:
        return "why"
    return None


def is_followup(question: str) -> bool:
    """Short and pointing at something said before ("what about the mask then?", "why is that?")."""
    words = question.split()
    return len(words) <= 6 and bool(ANAPHORA.search(question))


def kind_preference(question: str) -> set[str]:
    """Which kind of passage best answers this phrasing: a definition, a reason, a failure, ..."""
    q = question.lower()
    if re.search(r"\b(removed|remove|without|skip|missing|leave out)\b", q):
        return {"breaks"}
    if re.search(r"\b(go wrong|goes wrong|set up wrong|misconfigur|bad(ly)?|mistake)\b", q):
        return {"misconfigured"}
    if q.startswith("why") or "needed" in q or "purpose" in q:
        return {"why"}
    if re.search(r"\b(what|how) (does|do|is|are|did)\b", q):
        return {"what", "claim"}
    return set()
