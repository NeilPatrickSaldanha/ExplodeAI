"""What breaks if a stage is removed? Run the real pipeline without it and see.

`ablate(params, stage)` executes every remaining stage for real and returns a
compact outcome. Removing a stage means the work it does never happens; the
rest of the pipeline runs unchanged and does the best it can with what it gets:

- corpus          no documents exist, so there is nothing to chunk or search.
- chunker         each whole document is passed on as a single chunk.
- embedder        chunks are never turned into vectors; dense scoring is
                  impossible. BM25 needs no embeddings, so it still works.
- vector_index    nothing is stored, so there is nothing to search.
- query_encoder   the question is never embedded; dense scoring is impossible.
                  BM25 matches the raw question text, so it still works.
- retriever       nothing is ranked: chunks reach the prompt in corpus order
                  until the context budget runs out.
- prompt_builder  the generator receives only the question, with no documents.
- generator       the prompt is built but never answered.

These statements describe ExplodeAI's own pipeline and are checked by
tests/test_ablation.py, not by external citations.
"""

from app.experiments.rag.chunking import Chunk, chunk_corpus
from app.experiments.rag.corpus import get_corpus
from app.experiments.rag.embedding import make_embedder
from app.experiments.rag.generation import NO_ANSWER, assemble_prompt, extractive_answer
from app.experiments.rag.pipeline import STAGES, RagParams
from app.experiments.rag.retrieval import BM25, dense_scores, rank, rrf


def ablate(params: RagParams, stage: str | None) -> dict:
    if stage is not None and stage not in STAGES:
        raise ValueError(f"unknown stage '{stage}'")
    notes: list[str] = []

    docs = [] if stage == "corpus" else get_corpus(params.corpus_id)
    if stage == "chunker":
        chunks = [Chunk(f"{d.id}#0", d.id, 0, d.text, 0, len(d.text)) for d in docs]
        notes.append(f"{len(chunks)} whole documents passed on as chunks")
    else:
        chunks = chunk_corpus(docs, params.strategy, params.chunk_size, params.overlap)
    texts = [c.text for c in chunks]

    has_chunk_vectors = bool(chunks) and stage not in ("embedder",)
    has_index = bool(chunks) and stage != "vector_index"
    has_query_vector = stage != "query_encoder"

    ranked: list[Chunk]
    if not has_index:
        ranked = []
        notes.append("nothing is stored to search" if chunks else "no documents to search")
    elif stage == "retriever":
        ranked = list(chunks)  # unranked: corpus order, every chunk
        notes.append("chunks are not ranked; they arrive in corpus order")
    else:
        dense = None
        if has_chunk_vectors and has_query_vector:
            emb = make_embedder(params.embedder)
            emb.fit(texts)
            dense = rank(dense_scores(emb.embed(texts), emb.embed([params.query])[0]))
        elif params.method in ("dense", "hybrid"):
            notes.append("dense scoring is impossible without both chunk and query vectors")
        lexical = rank(BM25(texts).scores(params.query)) if params.method in ("bm25", "hybrid") else None
        if params.method == "dense":
            final = dense or []
        elif params.method == "bm25":
            final = lexical
        else:
            final = rank(rrf([r for r in (dense, lexical) if r], len(chunks))) if (dense or lexical) else []
        ranked = [chunks[h.index] for h in final[: params.top_k]]

    if stage == "prompt_builder":
        prompt = assemble_prompt(params.query, [], params.context_budget_words)
        notes.append("the generator receives only the question")
    else:
        prompt = assemble_prompt(params.query, ranked, params.context_budget_words)

    in_context = [c for c in ranked if c.id in prompt.included]
    if stage == "generator":
        answer_text, has_answer = None, False
        notes.append("the prompt is built but never answered")
    else:
        sentences = extractive_answer(params.query, in_context)
        answer_text = " ".join(f"{s.text} [{s.source}]" for s in sentences) or NO_ANSWER
        has_answer = bool(sentences)

    return {
        "removed": stage,
        "chunks": len(chunks),
        "retrieved": [{"chunk_id": c.id, "text": c.text} for c in ranked[: max(params.top_k, 10)]],
        "prompt": {
            "included": prompt.included,
            "dropped": prompt.dropped,
            "context_words": prompt.context_words,
            "budget_words": params.context_budget_words,
        },
        "answer": {"text": answer_text, "has_answer": has_answer, "is_llm": False},
        "notes": notes,
    }
