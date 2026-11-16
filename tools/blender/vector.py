"""A vector drawn as a strip of number tiles: one tile per number, blue for positive, orange for negative.

The real vectors have 1024 numbers. A strip shows the first few and ends in "…", with the count printed.
"""

from blib import box, empty, ink, material, paper, plastic, text, tile_color, vector_values
from colors import CARD, INK

TILE = 0.019
GAP = 0.004


def strip(name, parent, loc, n=20, seed=1, frame=(232, 236, 242), count_label="1024 numbers", rot=(0, 0, 0), explode=None, rows=1):
    """A bar of number tiles lying in its own XY plane, facing +Z, starting at loc and running along +X."""
    g = empty(name, loc, parent, explode)
    g.rotation_euler = rot
    length = n * (TILE + GAP) + GAP + 0.03
    height = rows * (TILE + GAP) + GAP
    box(f"{name}_bar", (length, height, 0.006), (length / 2, 0, 0), material("bar", frame, rough=0.35, coat=0.3), g, bevel=0.002)
    values = vector_values(seed, n * rows)
    for r in range(rows):
        for i in range(n):
            v = float(values[r * n + i])
            x = GAP + TILE / 2 + i * (TILE + GAP)
            y = (rows - 1) / 2 * (TILE + GAP) - r * (TILE + GAP)
            box(f"{name}_t{r}_{i}", (TILE, TILE, 0.006), (x, y, 0.005), plastic(tile_color(v)), g, bevel=0.0025)
    text(f"{name}_more", "…", 0.03, (length - 0.016, 0, 0.004), ink(INK), g)
    if count_label:
        # Printed on a paper tag, so it reads on any background.
        tag_w = 0.012 * len(count_label) + 0.02
        box(f"{name}_tag", (tag_w, 0.03, 0.003), (tag_w / 2, -height / 2 - 0.02, 0.0), paper(CARD), g, bevel=0.001)
        text(f"{name}_count", count_label, 0.016, (0.01, -height / 2 - 0.02, 0.0022), ink(INK), g, align="LEFT")
    return g
