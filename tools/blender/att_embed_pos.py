"""Attention stage 2, Vectors + position: a word's vector plus a position pattern gives the vector attention uses.

Three strips for the word "cat" (position 1): its word vector, plus the position pattern (a wave that depends on
the position), equals the combined vector. Real values (the first six of 64 numbers).
"""

import math

from blib import box, empty, ink, plastic, text, tile_color, wedge
from colors import INK
from shapes import data, led, nameplate, sphere
from vector import GAP, TILE


def build():
    d = data("attention")
    root = empty("embed_pos")
    top = wedge("slope", 1.2, 0.66, 30, root)
    emb = d["embedding"]
    rows = [("word vector (cat)", emb["word_preview"][1], 0.2), ("position pattern (place 1)", emb["position_preview"][1], 0.0), ("added together", emb["input_preview"][1], -0.2)]
    for name, vals, y in rows:
        g = empty(name, (-0.5, y, 0.003), top, explode=(0, 0, 0.02))
        n = len(vals)
        length = n * (TILE + GAP) + GAP + 0.045
        box("bar", (length, TILE + 2 * GAP, 0.006), (length / 2, 0, 0.003), ink((232, 236, 242)), g, bevel=0.002)
        for i, v in enumerate(vals):
            box(f"t{i}", (TILE, TILE, 0.006), (GAP + TILE / 2 + i * (TILE + GAP), 0, 0.007), plastic(tile_color(float(v))), g, bevel=0.0025)
        text("lbl", name, 0.036, (length + 0.03, 0, 0.004), ink(INK), g, align="LEFT")
    nameplate("plus", "+", top, (-0.62, 0.1, 0.004), 0.08, 0.08, 0.07)
    nameplate("eq", "=", top, (-0.62, -0.1, 0.004), 0.08, 0.08, 0.07)
    for k in range(40):
        sphere(f"b{k}", 0.008, (0.12 + k * 0.011, 0.05 * math.sin(k * 0.5), 0.02), led((255, 190, 80), 3.0), top, 8)
    return root
