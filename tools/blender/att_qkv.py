"""Attention stage 3, Q K V: each word makes a query, a key and a value (here for "cat", head 1).

Query (blue, a magnifying glass): what it looks for. Key (orange, a key): what it offers. Value (green, a
box): what it hands over. Real values (the first six numbers).
"""

from blib import box, cylinder, empty, ink, plastic, text, tile_color, wedge
from colors import INK
from shapes import brass, data, steel, torus
from vector import GAP, TILE

QCOL, KCOL, VCOL = (47, 111, 214), (224, 154, 27), (46, 158, 91)


def row(top, name, vals, y, col, label):
    g = empty(name, (-0.3, y, 0.003), top, explode=(0.05, 0, 0.02))
    n = len(vals)
    length = n * (TILE + GAP) + GAP + 0.045
    box("bar", (length, TILE + 2 * GAP, 0.006), (length / 2, 0, 0.003), plastic(col), g, bevel=0.002)
    for i, v in enumerate(vals):
        box(f"t{i}", (TILE, TILE, 0.006), (GAP + TILE / 2 + i * (TILE + GAP), 0, 0.007), plastic(tile_color(float(v))), g, bevel=0.0025)
    text("lbl", label, 0.044, (length + 0.03, 0, 0.004), ink(INK), g, align="LEFT")


def build():
    d = data("attention")
    root = empty("qkv")
    top = wedge("slope", 1.25, 0.7, 30, root)
    h = d["heads"][0]
    i = 1  # "cat"
    row(top, "q", h["q"][i], 0.22, QCOL, "query: what I look for")
    row(top, "k", h["k"][i], 0.0, KCOL, "key: what I offer")
    row(top, "v", h["v"][i], -0.22, VCOL, "value: what I hand over")
    mg = empty("magnifier", (-0.45, 0.22, 0.03), top)
    torus("rim", 0.05, 0.008, (0, 0, 0.0), steel(), mg)
    cylinder("handle", 0.008, 0.06, (0.05, -0.05, 0.0), brass(), mg, rot=(0, 1.5708, 0.785))
    key = empty("key", (-0.45, 0.0, 0.03), top)
    torus("bow", 0.03, 0.008, (-0.03, 0, 0), brass(), key)
    box("shaft", (0.09, 0.012, 0.012), (0.04, 0, 0), brass(), key)
    box("tooth", (0.012, 0.03, 0.012), (0.07, -0.02, 0), brass(), key)
    cube = empty("cube", (-0.45, -0.22, 0.04), top)
    box("b", (0.07, 0.07, 0.07), (0, 0, 0), plastic(VCOL), cube, bevel=0.008)
    return root
