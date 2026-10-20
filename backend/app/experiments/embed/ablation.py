"""What breaks if an embeddings stage is removed? Run the real pipeline without it.

- library         nothing to compare against, so there are no neighbours.
- your_text       nothing to embed, so there are no neighbours.
- tokenizer       the model only reads token ids, so raw text produces no vectors.
- encoder         token ids exist, but no vectors are computed from them.
- pooling         the encoder gives one vector per token, not one per text, so
                  texts of different lengths cannot be compared as a whole.
- normalizer      vectors keep their raw lengths, so dot-product scores are no
                  longer bounded between -1 and 1 (cosine itself is unaffected).
- similarity      nothing is ranked: the library comes back in its stored order.
- semantic_space  no 3D map is drawn, yet nearest neighbours are unchanged: the
                  map is only a view of the real vectors.

These statements describe ExplodeAI's own pipeline and are checked by
tests/test_embed_ablation.py.
"""

import numpy as np

from app.experiments.embed import model as bge
from app.experiments.embed.corpus import get_library
from app.experiments.embed.pipeline import STAGES, EmbedParams, _library_neural, score

TOP = 3


def ablate(params: EmbedParams, stage: str | None) -> dict:
    if stage is not None and stage not in STAGES:
        raise ValueError(f"unknown stage '{stage}'")
    notes: list[str] = []
    library = [] if stage == "library" else get_library(params.library_id)
    text = "" if stage == "your_text" else params.text
    query_text = (bge.QUERY_INSTRUCTION if params.query_instruction else "") + text

    def outcome(neighbours=None, vectors=None, query_dim=None, score_range=None, token_vectors=None,
                has_map=True):
        neighbours = neighbours or []
        return {
            "removed": stage,
            "library_vectors": vectors,
            "query_vector_dim": query_dim,
            "token_vectors": token_vectors,
            "neighbours": neighbours,
            "top_category": neighbours[0]["category"] if neighbours else None,
            "score_range": score_range,
            "has_map": has_map,
            "notes": notes,
        }

    if stage == "library":
        notes.append("no library, so nothing to compare against")
        return outcome()
    if not text:
        notes.append("no text, so nothing to embed")
        return outcome()
    enc = bge.get_encoder()
    if stage == "tokenizer":
        notes.append("the model reads token ids, not raw text, so no vectors are produced")
        return outcome()
    encoded = enc.encode([query_text])
    if stage == "encoder":
        notes.append(f"{len(encoded.ids[0])} token ids, but nothing turns them into vectors")
        return outcome()
    hidden = encoded.hidden[0]
    if stage == "pooling":
        notes.append(f"{hidden.shape[0]} token vectors and no single text vector, "
                     "so texts cannot be compared")
        return outcome(token_vectors=f"{hidden.shape[0]} × {hidden.shape[1]}")

    lib_raw, _ = _library_neural(params.library_id, params.pooling)
    q_raw = bge.pool(hidden, params.pooling)
    if stage == "normalizer":
        q, lib, metric = q_raw, lib_raw, "dot" if params.metric != "cosine" else "cosine"
        notes.append("vectors keep their raw length")
    else:
        q, lib, metric = bge.l2_normalize(q_raw), bge.l2_normalize(lib_raw), params.metric
        if stage is None and not params.normalize:
            q, lib = q_raw, lib_raw
    scores = score(q, lib, metric)
    if stage == "similarity":
        order = list(range(len(library)))
        notes.append("nothing is ranked: the library comes back in stored order")
        shown = [{"id": library[i].id, "category": library[i].category, "score": None} for i in order[:TOP]]
        return outcome(shown, f"{lib.shape[0]} × {lib.shape[1]}", int(q.shape[0]))
    order = sorted(range(len(library)), key=lambda i: (-scores[i], i))
    shown = [{"id": library[i].id, "category": library[i].category, "score": round(float(scores[i]), 4)}
             for i in order[:TOP]]
    has_map = stage != "semantic_space"
    if not has_map:
        notes.append("no 3D map is drawn, but the neighbours are unchanged")
    return outcome(shown, f"{lib.shape[0]} × {lib.shape[1]}", int(q.shape[0]),
                   [round(float(np.min(scores)), 3), round(float(np.max(scores)), 3)], has_map=has_map)
