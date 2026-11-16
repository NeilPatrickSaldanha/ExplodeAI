"""Attention stage 5, Mask: the same 6 x 6 grid; the 15 cells above the diagonal are covered.

A word may only look at itself and the words before it. The covered cells (dark hatched plates) are the
future: 15 of 36 cells.
"""

import numpy as np

from att_scores import heat
from blib import box, empty, ink, plastic, text, wedge
from colors import INK
from shapes import data, nameplate


def build():
    d = data("attention")
    root = empty("mask")
    top = wedge("slope", 1.0, 0.9, 32, root)
    words = d["tokens"]
    s = np.array(d["heads"][0]["scores"])
    lo, hi = s.min(), s.max()
    cell = 0.115
    for r in range(6):
        for c in range(6):
            g = empty(f"c{r}{c}", ((c - 2.5) * cell, (2.5 - r) * cell - 0.02, 0.003), top, explode=(0, 0, 0.0 if c <= r else 0.05))
            if c > r:
                box("cover", (cell - 0.01, cell - 0.01, 0.07), (0, 0, 0.035), plastic((52, 56, 68)), g, bevel=0.005)
                for k in (-1, 0, 1):
                    b = box(f"h{k}", (cell * 0.9, 0.008, 0.004), (0, k * 0.03, 0.0725), ink((150, 156, 170)), g)
                    b.rotation_euler = (0, 0, 0.785)
            else:
                v = (s[r, c] - lo) / (hi - lo)
                h = 0.02 + 0.2 * v
                box("col", (cell - 0.014, cell - 0.014, h), (0, 0, h / 2), plastic(heat(v)), g, bevel=0.004)
        text(f"row{r}", words[r], 0.032, (-3.0 * cell, (2.5 - r) * cell - 0.02, 0.01), ink((236, 238, 244)), top, align="RIGHT")
    nameplate("lbl", "15 of 36 hidden", top, (0, -3.3 * cell, 0.006), 0.4, 0.05, 0.034)
    return root
