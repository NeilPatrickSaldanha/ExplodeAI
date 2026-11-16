"""Tokenization stage 7, Encoder: 35 byte tiles glued, in the order they were learned, into 8 tokens.

Top row: the 35 starting symbols. Bottom row: the 8 tokens with their real ids
(262, 269, 346, 258, 275, 285, 321, 46). Arrows show which symbols became which token.
"""

from blib import box, empty, ink, text, wedge
from colors import INK
from shapes import PALETTE8, WALNUT, arrow, data, letter_tile, nameplate, wood, brass

SMALL = 0.03


def build():
    d = data("tokenization")
    root = empty("encoder")
    top = wedge("slope", 1.18, 0.62, 34, root)
    text_s = d["text"]
    total = len(text_s)
    x0 = -total * SMALL / 2 + SMALL / 2
    # which token each character belongs to
    owner = []
    for i, t in enumerate(d["tokens"]):
        owner += [i] * len(t["text"])
    for k, ch in enumerate(text_s):
        letter_tile(f"b{k}", ch, top, (x0 + k * SMALL, 0.2, 0.003), SMALL, explode=(0, 0, 0))
    # token blocks, sized to the characters they replace
    pos = 0
    gap = 0.024
    widths = [len(t["text"]) * SMALL for t in d["tokens"]]
    full = sum(widths) + gap * (len(widths) - 1)
    x = -full / 2
    for i, t in enumerate(d["tokens"]):
        w = widths[i]
        cx = x + w / 2
        g = empty(f"tok{i}", (cx, -0.12, 0.003), top, explode=(0, -0.03, 0.03))
        box(f"tok{i}_b", (w, 0.1, 0.03), (0, 0, 0.015), wood((236, 214, 170)), g, bevel=0.007)
        box(f"tok{i}_c", (w, 0.014, 0.004), (0, 0.043, 0.031), ink(PALETTE8[i]), g)
        text(f"tok{i}_t", t["text"].replace(" ", "·"), 0.034, (0, 0.004, 0.033), ink(INK), g)
        nameplate(f"tok{i}_id", str(t["id"]), g, (0, -0.075, 0.003), max(w, 0.07), 0.04, 0.03)
        first = x0 + pos * SMALL
        last = x0 + (pos + len(t["text"]) - 1) * SMALL
        box(f"bridge{i}", (last - first + SMALL, 0.008, 0.004), ((first + last) / 2, 0.17, 0.004), ink(PALETTE8[i]), top)
        arrow(f"ar{i}", top, ((first + last) / 2, 0.165, 0.004), (cx, -0.055), PALETTE8[i], 0.006)
        pos += len(t["text"])
        x += w + gap
    return root
