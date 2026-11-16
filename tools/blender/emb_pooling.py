"""Embeddings stage 5, Pooling: 8 token vectors, and the [CLS] row (gold) lifted out as the sentence vector.

The model was trained to treat the [CLS] vector as the summary, so pooling keeps that row.
"""

from blib import box, empty, ink, wedge
from colors import GOLD, INK
from shapes import data, nameplate
from vector import strip


def build():
    d = data("embeddings")
    root = empty("pooling")
    top = wedge("slope", 1.1, 0.62, 32, root)
    for i, t in enumerate(d["tokens"]):
        y = 0.22 - i * 0.065
        cls = i == 0
        g = empty(f"row{i}", (-0.4, y, 0.003), top, explode=(0.05, 0.0, 0.0) if cls else None)
        strip(f"v{i}", g, (0, 0, 0.004), n=12, seed=300 + i, count_label="", rows=1)
        nameplate(f"l{i}", t["text"], g, (-0.1, 0, 0.003), 0.15, 0.038, 0.028, face=GOLD if cls else (214, 218, 226))
        if cls:
            box("hl", (0.66, 0.06, 0.004), (0.26, 0, 0.0), ink(GOLD), g, bevel=0.003)
    nameplate("out", "1 x 384", top, (0.3, 0.22, 0.004), 0.2, 0.06, 0.04, face=GOLD)
    return root
