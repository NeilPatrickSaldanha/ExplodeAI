"""Attention stage 4, Score grid: every query against every key, a 6 x 6 grid; column height is the score.

Real scaled scores for "the cat sat on the mat", head 1. Warm columns are high scores, cool columns low.
Rows are the words asking; columns are the words being looked at.
"""

import numpy as np

from blib import box, empty, ink, plastic, text, wedge
from colors import INK
from shapes import data


def heat(t):
    stops = [(48, 74, 146), (46, 150, 160), (240, 205, 70), (214, 69, 62)]
    t = max(0.0, min(1.0, t)) * 3
    i = min(2, int(t))
    f = t - i
    return tuple(int(stops[i][k] + (stops[i + 1][k] - stops[i][k]) * f) for k in range(3))


def build():
    d = data("attention")
    root = empty("score_grid")
    top = wedge("slope", 1.0, 0.86, 32, root)
    words = d["tokens"]
    s = np.array(d["heads"][0]["scores"])
    lo, hi = s.min(), s.max()
    cell = 0.115
    for r in range(6):
        for c in range(6):
            v = (s[r, c] - lo) / (hi - lo)
            h = 0.02 + 0.2 * v
            g = empty(f"c{r}{c}", ((c - 2.5) * cell, (2.5 - r) * cell - 0.02, 0.003), top)
            box("col", (cell - 0.014, cell - 0.014, h), (0, 0, h / 2), plastic(heat(v)), g, bevel=0.004)
        text(f"row{r}", words[r], 0.032, (-3.0 * cell, (2.5 - r) * cell - 0.02, 0.01), ink((236, 238, 244)), top, align="RIGHT")
        text(f"col{r}", words[r], 0.032, ((r - 2.5) * cell, 3.1 * cell - 0.02, 0.01), ink((236, 238, 244)), top)
    return root
