"""Embeddings stage 6, Normalizer: the vector's length goes from 9.25 to exactly 1.

Two bars on a ruler: the raw vector (long, orange) and the same vector divided by its length (short, blue).
Only the direction is kept; the length becomes 1, so cosine and dot product agree.
"""

from blib import box, empty, ink, text, wedge
from colors import INK, NEG, POS
from shapes import arrow, brass, data, nameplate, steel


def build():
    d = data("embeddings")
    root = empty("normalizer")
    top = wedge("slope", 1.2, 0.5, 30, root)
    L = 1.0  # ruler length for 10 units
    unit = L / 10
    box("ruler", (L + 0.04, 0.07, 0.01), (0, -0.04, 0.008), steel(), top, bevel=0.004)
    for k in range(11):
        box(f"tick{k}", (0.004, 0.03 if k % 5 == 0 else 0.018, 0.004), (-L / 2 + k * unit, -0.04, 0.0145), ink((236, 238, 244)), top)
        if k % 5 == 0:
            text(f"n{k}", str(k), 0.03, (-L / 2 + k * unit, -0.1, 0.0125), ink((236, 238, 244)), top)
    nb = d["norm_before"]
    box("before", (nb * unit, 0.07, 0.04), (-L / 2 + nb * unit / 2, 0.08, 0.02), ink(NEG), top, bevel=0.006)
    box("after", (1 * unit, 0.07, 0.04), (-L / 2 + unit / 2, 0.22, 0.02), ink(POS), top, bevel=0.006)
    arrow("div", top, (-L / 2 + nb * unit + 0.03, 0.08, 0.005), (-L / 2 + unit + 0.03, 0.22), INK, 0.012)
    nameplate("l1", f"{nb:.2f}", top, (-L / 2 + nb * unit + 0.12, 0.08, 0.006), 0.16, 0.055, 0.04, face=NEG, ink_c=(255, 255, 255))
    nameplate("l2", "1.00", top, (-L / 2 + unit + 0.14, 0.22, 0.006), 0.16, 0.055, 0.04, face=POS, ink_c=(255, 255, 255))
    return root
