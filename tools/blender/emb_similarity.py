"""Embeddings stage 7, Similarity: the 10 nearest library sentences as columns; height is the score.

Real scores for "a place to put my books": the bookshelf (0.695), desk (0.566), armchair (0.554) lead.
Column colours are the topics, as everywhere in this lesson.
"""

from blib import box, empty, ink, plastic, text, wedge
from colors import GOLD, INK
from emb_library import TOPIC
from shapes import data, nameplate


def build():
    d = data("embeddings")
    root = empty("similarity")
    top = wedge("slope", 1.2, 0.6, 30, root)
    nb = d["neighbours"][:10]
    H = 0.4
    for i, n in enumerate(nb):
        x = (i - 4.5) * 0.105
        h = max(0.02, n["score"] / nb[0]["score"] * H)
        g = empty(f"col{i}", (x, 0.0, 0.003), top, explode=(0, 0.0, 0.03))
        box("c", (0.08, 0.08, h), (0, 0, h / 2), plastic(TOPIC[n["category"]]), g, bevel=0.006)
        if i < 3:
            box("cap", (0.088, 0.088, 0.012), (0, 0, h + 0.006), plastic(GOLD), g, bevel=0.004)
        text("s", f"{n['score']:.3f}", 0.03, (0, -0.1, 0.006), ink((236, 238, 244)), top, rot=(0, 0, 0)).location.x = x
        nameplate("rk", str(i + 1), g, (0, -0.15, 0.004), 0.06, 0.05, 0.034, face=GOLD if i < 3 else (214, 218, 226))
    return root
