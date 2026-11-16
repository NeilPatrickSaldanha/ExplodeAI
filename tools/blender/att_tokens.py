"""Attention stage 1, Words in: "the cat sat on the mat" as six wooden word blocks, numbered 0 to 5.

The word "the" appears twice (positions 0 and 4) and gets the same colour both times.
"""

from blib import box, empty, ink, text, wedge
from colors import INK
from shapes import PALETTE8, data, nameplate, wood


def build():
    d = data("attention")
    root = empty("words_in")
    top = wedge("slope", 1.25, 0.5, 32, root)
    words = d["tokens"]
    colour = {}
    for w in words:
        colour.setdefault(w, PALETTE8[len(colour)])
    for i, w in enumerate(words):
        x = (i - (len(words) - 1) / 2) * 0.2
        g = empty(f"w{i}", (x, 0.02, 0.003), top, explode=(0, 0.02, 0.04))
        wd = 0.17
        box("blk", (wd, 0.14, 0.07), (0, 0, 0.035), wood((236, 214, 170)), g, bevel=0.012)
        box("band", (wd, 0.03, 0.074), (0, -0.055, 0.037), ink(colour[w]), g, bevel=0.006)
        text("t", w, 0.056, (0, 0.012, 0.0745), ink(INK), g)
        nameplate("ix", str(i), g, (0, -0.11, 0.002), 0.07, 0.05, 0.036)
    return root
