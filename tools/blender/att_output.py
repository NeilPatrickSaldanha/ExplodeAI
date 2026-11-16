"""Attention stage 8, Heads + output: two heads of 32 numbers are joined into 64 and mixed by one more matrix.

Head 1 and head 2 (each 32 numbers) sit side by side to make one 64-number vector, then pass through a
final plate (the output matrix) to give the new vector for each word. Real values (first numbers shown).
"""

from blib import box, empty, ink, plastic, text, tile_color, wedge
from colors import INK
from shapes import arrow, data, nameplate, steel
from vector import GAP, TILE


def strip_vals(parent, name, vals, loc, col):
    g = empty(name, loc, parent)
    n = len(vals)
    length = n * (TILE + GAP) + GAP + 0.03
    box("bar", (length, TILE + 2 * GAP, 0.006), (length / 2, 0, 0.003), plastic(col), g, bevel=0.002)
    for i, v in enumerate(vals):
        box(f"t{i}", (TILE, TILE, 0.006), (GAP + TILE / 2 + i * (TILE + GAP), 0, 0.007), plastic(tile_color(float(v))), g, bevel=0.0025)
    return g


def build():
    d = data("attention")
    root = empty("output")
    top = wedge("slope", 1.25, 0.6, 30, root)
    strip_vals(top, "head1", d["heads"][0]["v"][2][:5], (-0.5, 0.15, 0.003), (47, 111, 214))
    strip_vals(top, "head2", d["heads"][1]["v"][2][:5], (-0.5, 0.0, 0.003), (46, 158, 91))
    nameplate("h1", "head 1: 32", top, (-0.6, 0.15, 0.004), 0.2, 0.045, 0.028)
    nameplate("h2", "head 2: 32", top, (-0.6, 0.0, 0.004), 0.2, 0.045, 0.028)
    arrow("a1", top, (-0.1, 0.15, 0.004), (0.05, 0.08), INK, 0.012)
    arrow("a2", top, (-0.1, 0.0, 0.004), (0.05, 0.05), INK, 0.012)
    j = empty("joined", (0.07, 0.06, 0.003), top, explode=(0.03, 0, 0.03))
    box("bar", (0.55, 0.075, 0.01), (0.275, 0, 0.005), plastic((230, 234, 240)), j, bevel=0.004)
    text("lbl", "joined: 64 numbers", 0.034, (0.345, -0.07, 0.004), ink((236, 238, 244)), top)
    plate = empty("matrix", (0.45, -0.12, 0.003), top, explode=(0, 0, 0.05))
    box("p", (0.4, 0.14, 0.02), (0, 0, 0.01), steel(), plate, bevel=0.01)
    text("t", "output matrix", 0.036, (0, 0, 0.0215), ink(INK), plate)
    nameplate("out", "new vector: 64 numbers", top, (0.45, -0.28, 0.004), 0.5, 0.05, 0.03)
    return root
