"""Tokenization stage 4, Merge learner: the first three real merges, most common pair first.

Each row: the two tiles that were side by side, an arrow, the new token with its new id, and a bar showing how
many times the pair was seen in the corpus (48, 40, 28 in a default run).
"""

from blib import box, empty, ink, text, wedge
from colors import INK
from shapes import MAPLE, PALETTE8, arrow, brass, data, nameplate, wood

CW = 0.06  # width per character on a tile


def tile(name, label, parent, loc, color, explode=None, edge=False):
    w = CW * len(label) + 0.05
    g = empty(name, loc, parent, explode)
    box(f"{name}_b", (w, 0.1, 0.026), (0, 0, 0.013), wood(color), g, bevel=0.006)
    if edge:
        box(f"{name}_e", (w + 0.014, 0.114, 0.006), (0, 0, 0.003), brass(), g, bevel=0.004)
    text(f"{name}_t", label.replace(" ", "·"), 0.062, (0, 0, 0.0275), ink(INK), g)
    return g, w


def build():
    d = data("tokenization")
    root = empty("merge_learner")
    top = wedge("slope", 1.5, 0.74, 34, root)
    steps = d["merges"][:3]
    for i, s in enumerate(steps):
        y = 0.22 - i * 0.22
        left, lw = tile(f"l{i}", s["left"], top, (-0.62, y, 0.003), MAPLE, explode=(-0.04, 0, 0))
        rw = CW * len(s["right"]) + 0.05
        right, _ = tile(f"r{i}", s["right"], top, (-0.62 + lw / 2 + rw / 2 + 0.012, y, 0.003), MAPLE)
        arrow(f"ar{i}", top, (-0.46, y, 0.004), (-0.24, y), INK, 0.014)
        m, mw = tile(f"m{i}", s["token"], top, (-0.12 + 0.07, y, 0.003), PALETTE8[i], explode=(0.03, 0.02, 0.02), edge=True)
        nameplate(f"id{i}", f"id {s['token_id']}", top, (0.14, y, 0.004), 0.2, 0.065, 0.04)
        bar = 0.62 * s["count"] / steps[0]["count"]
        box(f"bar{i}", (bar, 0.06, 0.016), (0.36 + bar / 2, y + 0.02, 0.008), ink(PALETTE8[i]), top, bevel=0.005)
        text(f"cnt{i}", f"seen {s['count']} times", 0.038, (0.36, y - 0.04, 0.004), ink((236, 238, 244)), top, align="LEFT")
    return root
