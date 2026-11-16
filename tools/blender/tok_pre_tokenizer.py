"""Tokenization stage 2, Pre-tokenizer: the sentence cut into its 8 word chunks.

Wooden letter tiles in two rows. A space stays glued to the front of the next word (the paler tile).
Each chunk has its own coloured bar underneath, and a steel blade stands in the first cut.
"""

import math

from blib import box, empty, ink, wedge
from colors import INK
from shapes import PALETTE8, WALNUT, data, letter_tile, steel, wood

TILE = 0.052
GAP = 0.03  # extra gap between chunks: where the cuts fall


def build():
    d = data("tokenization")
    chunks = d["pre_pieces"]  # ['The', ' keeper', ' lit', ' the', ' lantern', ' at', ' dusk', '.']
    root = empty("pre_tokenizer")
    top = wedge("slope", 1.12, 0.52, 34, root)
    rows = [chunks[:4], chunks[4:]]
    ci = 0
    cut = None
    for r, row in enumerate(rows):
        n = sum(len(c) for c in row) + (len(row) - 1) * GAP / TILE
        x = -n * TILE / 2 + TILE / 2
        y = 0.12 - r * 0.2
        for chunk in row:
            x0 = x
            for ch in chunk:
                letter_tile(f"t{ci}_{x:.3f}", ch, top, (x, y, 0.003), TILE, explode=(0, 0, 0))
                x += TILE
            w = len(chunk) * TILE
            box(f"bar{ci}", (w - 0.008, 0.012, 0.004), (x0 - TILE / 2 + w / 2, y - 0.045, 0.004), ink(PALETTE8[ci % 8]), top)
            if r == 0 and ci == 1:
                cut = x0 - TILE / 2 - GAP / 2
            x += GAP
            ci += 1
    blade = empty("blade", (cut, 0.12, 0.0), top, explode=(0, 0.04, 0.05))
    box("blade_steel", (0.006, 0.09, 0.1), (0, 0, 0.07), steel(), blade, bevel=0.0015)
    box("blade_handle", (0.02, 0.1, 0.03), (0, 0, 0.135), wood(WALNUT), blade, bevel=0.006)
    return root
