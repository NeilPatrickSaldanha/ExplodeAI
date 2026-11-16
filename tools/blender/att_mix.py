"""Attention stage 7, Weighted sum: the new vector for "sat" is a blend of the words' values.

Six glass tubes, one per word, filled to that word's attention share for the word "sat" (real weights),
all pouring into one flask. The more attention, the fuller the tube.
"""

import numpy as np

from blib import cylinder, empty, ink, plastic, text, wedge
from colors import INK
from shapes import PALETTE8, arrow, data, glass, nameplate


def build():
    d = data("attention")
    root = empty("mix")
    words = d["tokens"]
    w = np.array(d["weights_mean"])[2]  # "sat"
    colour = {}
    for t in words:
        colour.setdefault(t, PALETTE8[len(colour)])
    top = wedge("slope", 1.3, 0.55, 28, root)
    H = 0.3
    for i, t in enumerate(words):
        x = (i - 2.5) * 0.13 - 0.2
        g = empty(f"tube{i}", (x, 0.1, 0.003), top, explode=(0, 0, 0.03))
        cylinder("glass", 0.04, H, (0, 0, H / 2), glass(alpha=0.22), g, verts=20)
        lvl = max(0.012, H * w[i] / w.max() * 0.9)
        cylinder("liquid", 0.036, lvl, (0, 0, lvl / 2 + 0.004), plastic(colour[t]), g, verts=20)
        text("w", t, 0.032, (x, -0.075, 0.006), ink((236, 238, 244)), top)
        text("pc", f"{round(100 * w[i])}%", 0.03, (x, -0.115, 0.006), ink((236, 238, 244)), top)
    arrow("pour", top, (0.28, 0.1, 0.006), (0.4, 0.1), INK, 0.016)
    fl = empty("flask", (0.55, 0.1, 0.003), top, explode=(0.04, 0, 0.03))
    cylinder("belly", 0.09, 0.14, (0, 0, 0.07), glass(alpha=0.22), fl, verts=24)
    cylinder("neck", 0.03, 0.12, (0, 0, 0.19), glass(alpha=0.22), fl, verts=24)
    mix = tuple(int(sum(colour[words[i]][k] * w[i] for i in range(6)) / w.sum()) for k in range(3))
    cylinder("blend", 0.084, 0.1, (0, 0, 0.055), plastic(mix), fl, verts=24)
    nameplate("lbl", "new vector for 'sat'", top, (0.55, -0.12, 0.006), 0.36, 0.05, 0.03)
    return root
