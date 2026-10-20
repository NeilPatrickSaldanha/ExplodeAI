"""Tutor mode: a question about the stage you are on, then the grounded answer.

Questions are templates over each stage's own explanation, so every answer is lesson
content with its verified claims attached. No model writes them and none grades you.
"""

from fastapi import HTTPException

from app.content.loader import content
from app.content.schema import Component, Lesson


def _stage(lesson: Lesson, stage_id: str) -> Component:
    comp = next((c for c in lesson.components if c.id == stage_id), None)
    if comp is None or comp.explain is None:
        raise HTTPException(404, "stage not found")
    return comp


def questions_for(comp: Component) -> list[dict]:
    e = comp.explain
    assert e is not None
    ins = ", ".join(comp.inputs) or "nothing"
    outs = ", ".join(comp.outputs) or "nothing"
    return [
        {
            "kind": "io",
            "question": f"What goes into the {comp.label} step, and what comes out?",
            "answer": f"In: {ins}. Out: {outs}. {e.what}",
            "hint": "Open the stage and look at the Goes in / Comes out cards.",
        },
        {
            "kind": "why",
            "question": f"Why does the layer or pipeline need the {comp.label} step?",
            "answer": e.why,
            "hint": "Think about what the next step would be missing.",
        },
        {
            "kind": "breaks",
            "question": f"What would happen if the {comp.label} step were removed?",
            "answer": comp.breaks_if_removed or e.misconfigured,
            "hint": "You can check: use “Run without …” on the stage panel.",
        },
        {
            "kind": "wrong",
            "question": f"What can go wrong if {comp.label} is set up badly?",
            "answer": e.misconfigured,
            "hint": "Try the Experiment tab and change its settings.",
        },
        {
            "kind": "example",
            "question": f"Describe what happens to the data in {comp.label}, in your own words.",
            "answer": " ".join(e.happens),
            "hint": f"Analogy to start from: {e.analogy}",
        },
    ]


def check(lesson_id: str, stage_id: str, n: int) -> dict:
    _, lessons = content()
    lesson = lessons.get(lesson_id)
    if lesson is None:
        raise HTTPException(404, "lesson not found")
    comp = _stage(lesson, stage_id)
    qs = questions_for(comp)
    q = qs[n % len(qs)]
    return {
        **q,
        "lesson_id": lesson_id,
        "stage_id": stage_id,
        "stage_label": comp.label,
        "claim_ids": list(comp.explain.claims),
        "index": n % len(qs),
        "total": len(qs),
    }


def suggestions(lesson_id: str | None, stage_id: str | None) -> list[str]:
    _, lessons = content()
    lesson = lessons.get(lesson_id) if lesson_id else None
    comp = next((c for c in lesson.components if c.id == stage_id), None) if lesson and stage_id else None
    if comp:
        return [
            f"Why is the {comp.label} step needed?",
            f"What happens if {comp.label} is removed?",
            f"What can go wrong with {comp.label}?",
        ]
    if lesson:
        return [f"What is {lesson.title.split(',')[0]}?", f"What should I learn in Lesson {lesson.number}?"]
    return ["What is attention?", "Why do embeddings help search?", "How does RAG reduce hallucination?"]
