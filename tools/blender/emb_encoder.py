"""Embeddings stage 4, Encoder: 12 glass layers; the 8 tokens climb through all of them.

Eight glowing nodes per layer (one per token) are joined by rods running up through the whole stack, and
every layer lets each token be adjusted using the others. The result is an 8 x 384 table.
"""

from blib import box, cylinder, empty, ink, material, text
from colors import INK
from shapes import PALETTE8, glass, led, nameplate, sphere, steel

LAYERS = 12


def build():
    root = empty("encoder")
    w, dd = 0.9, 0.34
    for k in range(LAYERS):
        z = 0.03 + k * 0.045
        g = empty(f"layer{k}", (0, 0, z), root, explode=(0, 0, k * 0.012))
        box("plate", (w, dd, 0.012), (0, 0, 0), glass(), g, bevel=0.005)
        for i in range(8):
            x = (i - 3.5) * 0.1
            sphere(f"n{i}", 0.018, (x, 0, 0.012), led(PALETTE8[i], 3.0), g, 12)
    for i in range(8):
        x = (i - 3.5) * 0.1
        cylinder(f"rod{i}", 0.004, 0.03 + LAYERS * 0.045, (x, 0, (0.03 + LAYERS * 0.045) / 2), steel(), root, verts=8)
    nameplate("count", "12 layers", root, (0, -dd / 2 - 0.08, 0.04), 0.3, 0.06, 0.042, rot=(1.1, 0, 0))
    nameplate("shape", "8 tokens x 384 numbers", root, (0, -dd / 2 - 0.15, 0.012), 0.52, 0.05, 0.03, rot=(1.1, 0, 0))
    return root
