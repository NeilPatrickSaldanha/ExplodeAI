"""Tokenization stage 8, Decoder: ids looked up, bytes joined, text read back, round trip OK.

Top row: the 8 id plates. Bottom row: the sentence rebuilt, tile by tile. A green seal confirms the text
came back exactly (round trip: true, no unknown tokens).
"""

from blib import box, empty, ink, text, wedge
from colors import INK
from shapes import PALETTE8, arrow, check_seal, data, letter_tile, nameplate

SMALL = 0.03


def build():
    d = data("tokenization")
    root = empty("decoder")
    top = wedge("slope", 1.18, 0.62, 34, root)
    toks = d["tokens"]
    w = 0.12
    for i, t in enumerate(toks):
        x = (i - (len(toks) - 1) / 2) * (w + 0.012)
        nameplate(f"id{i}", str(t["id"]), top, (x, 0.21, 0.003), w, 0.05, 0.034)
        box(f"look{i}", (0.01, 0.07, 0.004), (x, 0.13, 0.004), ink(PALETTE8[i]), top)
    s = d["decoding"]["text"]
    x0 = -len(s) * SMALL / 2 + SMALL / 2
    for k, ch in enumerate(s):
        letter_tile(f"c{k}", ch, top, (x0 + k * SMALL, -0.02, 0.003), SMALL, explode=(0, 0, 0))
    seal = check_seal("seal", top, (-0.4, -0.22, 0.003), 0.08, True)
    text("rt", "round trip: same text, nothing unknown", 0.034, (0.12, -0.22, 0.004), ink((236, 238, 244)), top)
    return root
