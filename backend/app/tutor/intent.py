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
    r"how do i (start|begin|get started)|"
    r"^\s*(help|i need help|can (you|u) help( me)?|need help)\s*[!?.]*\s*$)",
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
# Questions about the conversation itself: "what did I just ask you?"
RECALL = re.compile(
    r"\bwhat\s+(did|have|was)\s+i\s+(just\s+|last\s+)?(ask|asked|asking|say|said|saying)\b|"
    r"\bwhat\s+(was|is|were)\s+(my|the)\s+(last\s+|previous\s+|earlier\s+|first\s+)?"
    r"(question|topic|thing\s+i\s+asked|message)s?\b(?!\s+(?:of|in)\s+(?:the\s+)?lesson)|"
    r"\bwhat\s+(are|were)\s+we\s+(just\s+)?(talking|discussing|chatting)\s+about\b|"
    r"\bwhat\s+(did|have)\s+we\s+(just\s+)?(talk|talked|discuss|discussed|cover|covered)\b|"
    r"\bremind\s+me\s+what\s+(i|we)\b|\bdo\s+(you|u)\s+remember\b|\bwhat\s+i\s+(just\s+)?asked\b",
    re.I,
)
RECALL_EMPTY = "We haven't talked about anything yet in this chat. Ask me about any of the four lessons."

NEEDS_TOPIC = (
    "Which part should I explain? Pick a stage or ask a question about it first, then ask me to simplify."
)


def classify(question: str) -> str | None:
    q = question.strip()
    if RECALL.search(q):
        return "recall"
    if ABOUT_ME.search(q):
        return "about_me"
    if GREETING.match(q):
        return "greeting"
    if THANKS.match(q) and not looks_like_question(q):
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
        return {"why", "claim"}  # a stage's "why" text, or a claim that gives the reason
    if re.match(r"^\s*(what\s+(is|are)\s+(an?\s+|the\s+)?\S+(\s+\S+)?\s*\??\s*$|define\b|meaning\s+of\b)", q):
        return {"what", "claim:definition"}  # "what is rag?": the definition first
    if re.search(r"\b(what|how) (does|do|is|are|did)\b", q):
        return {"what", "claim"}
    return set()


# ---------------------------------------------------------------- conversation-level understanding
# People open with greetings, slang and filler ("yooo whats good", "tell me in one line what is rag").
# These helpers peel that off so the real question (if any) is what gets searched.

_GREETING_PART = re.compile(
    r"^(?:(?:h+i+|h+e+y+(?:\s+there)?|hello+|hiya|howdy|greetings|yo+|o{2,}h*|sup|wa+s+u+p+|"
    r"what'?s\s+(?:good|up|poppin|happening|new)|whats\s+(?:good|up|poppin|happening|new)|"
    r"how\s+(?:are|r)\s+(?:you|u|ya)(?:\s+doing)?|how'?s\s+it\s+going|how\s+(?:you|u)\s+doing|"
    r"good\s+(?:morning|afternoon|evening|day)|nice\s+to\s+meet\s+(?:you|u)|hope\s+(?:you'?re|ur)\s+well)"
    r")(?![a-z'])(?:\s+(?:there|bro|man|dude|mate|friend|buddy|bot|tutor|explodeai)(?![a-z]))?[\s,.!?~]*",
    re.I,
)
GREETING_LEAD = "Hi!"
ABOUT_ME = re.compile(
    r"^(who|what)\s+(are|r)\s+(you|u)\b|^are\s+(you|u)\s+(a\s+)?(bot|ai|human|real|chatgpt|claude)|"
    r"^what'?s\s+your\s+name|^what\s+do\s+you\s+do\b",
    re.I,
)
ABOUT_ME_REPLY = (
    "I'm the ExplodeAI tutor. I answer questions about the four lessons (RAG, tokenization, embeddings and "
    "attention) using only their verified content, with the sources behind every fact. I can explain a stage "
    "simply, give an example, or quiz you."
)
SMALLTALK_FALLBACK = (
    "I'm here for questions about the four lessons. Try something like “what is RAG?”, “why do we normalise "
    "vectors?” or “explain the causal mask simply”, or ask “what are the lessons?”."
)
_QUESTION_WORD = re.compile(
    r"\b(what|whats|why|how|when|where|which|who|explain|define|describe|difference|does|do|is|are|can)\b",
    re.I,
)


def split_greeting(question: str) -> tuple[bool, str]:
    """('hi there, what is rag?') -> (True, 'what is rag?'); ('yooo whats good') -> (True, '')."""
    rest = question.strip()
    greeted = False
    for _ in range(4):
        m = _GREETING_PART.match(rest)
        if not m or not m.group(0).strip():
            break
        greeted = True
        rest = rest[m.end() :].strip()
    return greeted, rest


_FILLERS: list[tuple[str, str]] = [
    (r"\bwhat'?s\b", "what is"),
    (r"\bwat\b", "what"),
    (r"\bwhat\s+is\s+meant\s+by\b", "what is"),
    (r"\b(?:can|could|would|will)\s+(?:you|u)\s+(?:please\s+)?", ""),
    (r"\b(?:please|pls|plz)\b", ""),
    (r"\b(?:tell|show|give)\s+me\b", ""),
    (r"\b(?:explain|describe|summari[sz]e)\b(?:\s+to\s+me)?", ""),
    (r"\b(?:in\s+)?(?:one|1|a\s+single|just\s+one)\s+(?:line|sentence|word)s?\b\s*[:,-]?", ""),
    (r"\bin\s+a\s+(?:line|sentence|word)\b", ""),
    (
        r"\b(?:briefly|quickly|simply|real\s+quick|in\s+short|tl;?\s*dr|in\s+simple\s+(?:words|terms)|"
        r"in\s+plain\s+(?:english|words))\b",
        "",
    ),
    (r"\bi\s+(?:want|wanna|would\s+like|need)\s+to\s+(?:know|understand)\b", ""),
    (r"\bdo\s+(?:you|u)\s+know\b", ""),
    (r"\b(?:for|to)\s+me\b", ""),
    (r"\bagain\b", ""),
]


_LEADING = re.compile(
    r"^(?:ok(?:ay)?|so|wait|um+|uh+|hmm+|alright|right|well|and|but|also|then)\b[\s,.]*", re.I
)


def clean(question: str) -> str:
    """The question without filler, for searching. Falls back to the original if nothing is left."""
    q = question.strip()
    for _ in range(4):
        q = _LEADING.sub("", q, count=1)
    for pattern, repl in _FILLERS:
        q = re.sub(pattern, repl, q, flags=re.I)
    q = re.sub(r"\s+", " ", q).strip(" ,.;:-")
    return q if len(q) >= 2 else question


BRIEF = re.compile(
    r"\b((?:in\s+)?(?:one|1|a\s+single|just\s+one)\s+(?:line|sentence)|in\s+a\s+(?:line|sentence)|briefly|tl;?\s*dr|in\s+short|short\s+answer|"
    r"quick(?:ly)?|one[-\s]liner|summar(?:y|ise|ize))\b",
    re.I,
)


def is_brief(question: str) -> bool:
    return bool(BRIEF.search(question))


# Words that only say "say it again differently" and carry no topic of their own.
_FOLLOWUP_WORDS = {
    "frame",
    "easier",
    "easy",
    "simpler",
    "simple",
    "simply",
    "word",
    "words",
    "again",
    "example",
    "examples",
    "more",
    "explain",
    "rephrase",
    "reword",
    "put",
    "way",
    "differently",
    "better",
    "term",
    "terms",
    "english",
    "plain",
    "dumb",
    "down",
    "break",
    "detail",
    "details",
    "elaborate",
    "expand",
    "matter",
    "matters",
    "why",
    "understand",
    "get",
    "confusing",
    "confused",
    "lost",
    "hard",
    "technical",
    "complicated",
    "eli5",
    "five",
    "kid",
    "like",
    "tell",
    "show",
    "give",
    "say",
    "said",
    "mean",
    "means",
    "meaning",
    "line",
    "sentence",
    "one",
}


# Everyday words that appear all over the lessons but do not say which topic is meant.
_GENERIC_WORDS = {
    "that",
    "this",
    "it",
    "its",
    "these",
    "those",
    "they",
    "them",
    "thi",
    "in",
    "of",
    "on",
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "for",
    "with",
    "about",
    "is",
    "are",
    "was",
    "be",
    "what",
    "how",
    "which",
    "me",
    "my",
    "you",
    "your",
    "i",
    "we",
    "matter",
    "matters",
    "mean",
    "means",
    "meaning",
    "really",
    "actually",
    "just",
    "wrong",
    "go",
    "goe",
    "goes",
    "work",
    "works",
    "happen",
    "happens",
    "need",
    "needed",
    "use",
    "used",
    "make",
    "set",
    "step",
    "stage",
    "part",
    "thing",
    "things",
    "good",
    "bad",
    "removed",
    "remove",
    "important",
    "doe",
    "do",
    "does",
    "can",
    "could",
    "would",
    "should",
    "point",
    "purpose",
    "role",
    "job",
    "here",
    "there",
    "now",
}


def has_topic(question: str, vocabulary: set[str]) -> bool:
    """Does the message name something the lessons cover, beyond follow-up and everyday words?"""
    from app.experiments.rag.text import terms

    return any(
        t in vocabulary and t not in _FOLLOWUP_WORDS and t not in _GENERIC_WORDS for t in terms(question)
    )


def looks_like_question(question: str) -> bool:
    return "?" in question or bool(_QUESTION_WORD.search(question))
