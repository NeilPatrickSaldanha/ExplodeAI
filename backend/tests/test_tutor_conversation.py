"""Real-world chat: slang greetings, filler words, one-line requests, follow-ups and small talk.

Each case is (message, lesson open, stage open, expected reply type, expected stage label or None).
The first block is the conversation a learner reported as broken; it must stay fixed.
"""

import pytest

H = {"X-Learner-Id": "conversation-test-01"}

GREETING = "chat"
CASES = [
    # Reported failures.
    ("ooo whats good", None, None, GREETING, None),
    ("yooo. whats good", None, None, GREETING, None),
    ("hi how are you what do you know", None, None, "overview", None),
    ("what does each lesson mean", None, None, "overview", None),
    ("tell me in one line what is rag", "embeddings", None, "answer", "Knowledge source"),
    ("what is rag", "embeddings", "library", "answer", "Knowledge source"),  # an open stage must not tip it
    ("what is bm25", "attention", "softmax", "answer", "Retriever"),
    # Greetings and small talk.
    ("hi", None, None, GREETING, None),
    ("yo", None, None, GREETING, None),
    ("hey there", None, None, GREETING, None),
    ("hello!", None, None, GREETING, None),
    ("hiya", None, None, GREETING, None),
    ("sup", None, None, GREETING, None),
    ("wassup bro", None, None, GREETING, None),
    ("good morning", None, None, GREETING, None),
    ("how are you", None, None, GREETING, None),
    ("how's it going?", None, None, GREETING, None),
    ("whats up", None, None, GREETING, None),
    ("who are you", None, None, GREETING, None),
    ("are you a bot?", None, None, GREETING, None),
    ("what's your name", None, None, GREETING, None),
    ("thanks!", None, None, GREETING, None),
    ("thank you so much", None, None, GREETING, None),
    ("ok", None, None, GREETING, None),
    ("cool", None, None, GREETING, None),
    ("lol", None, None, GREETING, None),
    ("help", None, None, GREETING, None),
    # Course overview.
    ("what are all four lessons", None, None, "overview", None),
    ("what lessons are there?", None, None, "overview", None),
    ("what can you teach me", None, None, "overview", None),
    # Plain questions.
    ("what is rag", None, None, "answer", "Knowledge source"),
    ("what is bm25?", None, None, "answer", "Retriever"),
    ("what is an embedding", None, None, "answer", "Similarity"),
    ("what is the causal mask?", "attention", "softmax", "answer", "Mask"),
    ("what is attention?", "embeddings", None, "answer", "Score grid"),
    ("whats bpe", None, None, "answer", None),
    ("what is hnsw", None, None, "answer", "Vector index"),
    ("why do we chunk documents", None, None, "answer", "Chunker"),
    ("why divide by the square root of d_k", None, None, "answer", "Score grid"),
    # Filler-laden questions.
    ("can you please explain the causal mask simply", "attention", None, "answer", "Mask"),
    ("okay so what is pooling", None, None, "answer", None),
    ("um what is bm25", None, None, "answer", "Retriever"),
    ("could you tell me what reciprocal rank fusion is", None, None, "answer", "Retriever"),
    ("i want to know what the kv cache is", None, None, "answer", None),
    ("explain chunk overlap for me", None, None, "answer", "Chunker"),
    ("do you know what hnsw is?", None, None, "answer", "Vector index"),
    # One-line requests.
    ("in one line, what is bm25", None, None, "answer", "Retriever"),
    ("briefly, what is the causal mask", None, None, "answer", "Mask"),
    ("one sentence: what is an embedding", None, None, "answer", "Similarity"),
    # Greeting plus question.
    ("hey what is rag", None, None, "answer", "Knowledge source"),
    ("yo whats bm25", None, None, "answer", "Retriever"),
    ("hi! can you explain the causal mask", "attention", None, "answer", "Mask"),
    # Stage-aware vague questions use the open stage.
    ("what can go wrong?", "attention", "softmax", "answer", "Softmax"),
    ("what does this step do?", "attention", "softmax", None, "Softmax"),
    ("why is it needed", "attention", "softmax", None, "Softmax"),
    # Off-topic stays refused.
    ("what is the capital of france", None, None, "none", None),
    ("write me a poem about cats", None, None, "none", None),
    ("who won the world cup", None, None, "none", None),
    ("how do i bake bread", None, None, "none", None),
]

ONE_LINE = {
    "tell me in one line what is rag",
    "in one line, what is bm25",
    "briefly, what is the causal mask",
    "one sentence: what is an embedding",
}


def stage_of(out):
    if out.get("plain"):
        return out["plain"].get("stage_label")
    return None


@pytest.mark.parametrize("message,lesson,stage,kind,label", CASES, ids=[c[0] for c in CASES])
def test_conversation(client, message, lesson, stage, kind, label):
    res = client.post(
        "/api/tutor/ask", json={"question": message, "lesson_id": lesson, "stage_id": stage}, headers=H
    )
    assert res.status_code == 200, res.text
    out = res.json()
    if kind == GREETING:
        assert out["type"] == "chat" and out["message"]
        return
    if kind is not None:
        assert out["type"] == kind, (out["type"], out.get("message"))
    if kind == "none":  # a refusal or a polite redirect, never lesson text
        assert out["type"] in ("none", "chat") and not out.get("sentences")
        return
    if label:
        assert stage_of(out) == label, stage_of(out)
    if message in ONE_LINE:
        assert len(out["sentences"]) == 1


def test_greeting_before_a_question_is_answered_with_a_lead(client):
    out = client.post("/api/tutor/ask", json={"question": "hey how are you, what is rag"}, headers=H).json()
    assert out["type"] == "answer" and out["lead"]


def test_follow_up_after_an_answer_uses_the_conversation(client):
    history = [{"question": "what is bm25", "stage_id": "retriever", "lesson_id": "rag-pipeline"}]
    out = client.post(
        "/api/tutor/ask", json={"question": "can you explain it simpler", "history": history}, headers=H
    ).json()
    assert out["type"] in ("plain", "answer") and stage_of(out) == "Retriever"


HISTORY = [
    {"question": "what is rag", "lesson_id": "rag-pipeline", "stage_id": "corpus"},
    {"question": "and why is it used", "lesson_id": "rag-pipeline", "stage_id": "corpus"},
    {"question": "what is bm25?", "lesson_id": "rag-pipeline", "stage_id": "retriever"},
]


@pytest.mark.parametrize(
    "message",
    [
        "what did i just ask you about",
        "what was the topic i asked you about just now",
        "what were we talking about",
        "do you remember what i asked",
        "what was my last question?",
        "remind me what we discussed",
    ],
)
def test_questions_about_the_conversation_are_answered_from_it(client, message):
    out = client.post("/api/tutor/ask", json={"question": message, "history": HISTORY}, headers=H).json()
    assert out["type"] == "chat"
    assert "“what is bm25”" in out["message"] and "Retriever, in Lesson 01" in out["message"]
    assert "Knowledge source" in out["message"], "earlier topics are listed too"


def test_recall_with_no_history_says_so(client):
    out = client.post("/api/tutor/ask", json={"question": "what did i just ask"}, headers=H).json()
    assert out["type"] == "chat" and "haven't talked" in out["message"]


def test_lesson_questions_that_mention_a_question_are_not_recall(client):
    out = client.post("/api/tutor/ask", json={"question": "what is the query in attention"}, headers=H).json()
    assert out["type"] == "answer"


@pytest.mark.parametrize(
    "message", ["'; DROP TABLE users; --", "<script>alert(1)</script>", "rm -rf / ; echo $HOME"]
)
def test_code_like_input_is_not_matched_against_the_lessons(client, message):
    out = client.post("/api/tutor/ask", json={"question": message}, headers=H).json()
    assert out["covered"] is False and out["sentences"] == [] and out["sources"] == []


def test_the_tutor_knows_about_every_lesson(client):
    from app.content.loader import content

    lessons = content()[1]
    about = (
        client.post("/api/tutor/ask", json={"question": "who are you"}, headers=H).json()["message"].lower()
    )
    keywords = {
        "rag-pipeline": "rag",
        "tokenization": "tokeniz",
        "embeddings": "embedding",
        "attention": "attention",
        "agents": "agents",
    }
    assert set(lessons) <= set(keywords), "a new lesson needs its name added to the tutor's about-me reply"
    for lesson_id, word in keywords.items():
        assert word in about, lesson_id
    for number in range(1, len(lessons) + 1):
        out = client.post(
            "/api/tutor/ask", json={"question": f"what is in lesson {number}"}, headers=H
        ).json()
        assert out["type"] == "overview" and out["focus_number"] == number
