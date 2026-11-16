"""Embeddings stage 3, Tokenizer: the sentence becomes 8 tokens with their real ids.

[CLS] (101) and [SEP] (102) are the special start and end markers (dark blocks).
"""

from blib import box, empty, ink, plastic, text, wedge
from colors import INK
from shapes import PALETTE8, data, nameplate


def build():
    d = data("embeddings")
    root = empty("tokenizer")
    top = wedge("slope", 1.3, 0.5, 32, root)
    toks = d["tokens"]
    w = 0.14
    for i, t in enumerate(toks):
        x = (i - (len(toks) - 1) / 2) * (w + 0.015)
        special = t["text"].startswith("[")
        col = (60, 66, 82) if special else (250, 247, 238)
        g = empty(f"tok{i}", (x, 0.04, 0.003), top, explode=(0, 0.02, 0.04))
        box("blk", (w, 0.12, 0.06), (0, 0, 0.03), plastic(col), g, bevel=0.01)
        box("cap", (w, 0.12, 0.012), (0, 0, 0.066), plastic(PALETTE8[i]), g, bevel=0.006)
        lbl = t["text"]
        text("t", lbl, 0.034 if len(lbl) < 6 else 0.026, (0, 0.0, 0.0735), ink((255, 255, 255) if special else INK), g)
        nameplate("id", str(t["id"]), g, (0, -0.105, 0.002), w, 0.045, 0.03)
    return root
