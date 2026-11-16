"""Stage 4, Card box: the index keeps all 11 vectors, each filed under the id of the chunk it came from.

A kraft file box with 11 file cards. Every card has a tab with its chunk id (in its article's colour)
and its vector strip printed along the top. The front card shows its strip in full.
"""

import math

from blib import box, empty, ink, material, paper, text
from cards import CHUNKS
from colors import CARD, DOC, INK, KRAFT
from vector import strip

IW, ID, IH = 0.64, 0.40, 0.15  # inner width, depth, wall height
T = 0.008


def build():
    root = empty("card_box")
    kraft = material("kraft", KRAFT, rough=0.85)
    box("floor", (IW + 2 * T, ID + 2 * T, T), (0, 0, T / 2), kraft, root, bevel=0.002)
    box("wall_back", (IW + 2 * T, T, IH), (0, ID / 2 + T / 2, IH / 2), kraft, root, bevel=0.002)
    box("wall_front", (IW + 2 * T, T, IH * 0.45), (0, -ID / 2 - T / 2, IH * 0.225), kraft, root, bevel=0.002)
    for s in (-1, 1):
        box(f"wall_side{s}", (T, ID + 2 * T, IH), (s * (IW / 2 + T / 2), 0, IH / 2), kraft, root, bevel=0.002)
    label_w = 0.2
    box("label", (label_w, 0.003, 0.04), (0, -ID / 2 - T - 0.0015, IH * 0.22), paper(CARD), root, bevel=0.001)
    text("label_text", "11 vectors", 0.02, (0, -ID / 2 - T - 0.0035, IH * 0.22), ink(INK), root, rot=(math.radians(90), 0, 0))

    n = len(CHUNKS)
    for i, (chunk_id, _) in enumerate(CHUNKS):
        y = -ID / 2 + 0.035 + i * (ID - 0.06) / (n - 1)
        g = empty(f"file_{chunk_id}", (0, y, T), root, explode=(0, 0.03 + i * 0.012, 0))
        g.rotation_euler = (math.radians(-10), 0, 0)
        box(f"{chunk_id}_file", (IW - 0.04, 0.003, IH * 0.92), (0, 0, IH * 0.46), paper(CARD), g, bevel=0.0008)
        tab_x = -0.24 + (i % 4) * 0.16
        top = IH * 0.92
        doc = chunk_id.split("#")[0]
        box(f"{chunk_id}_tab", (0.13, 0.003, 0.035), (tab_x, 0, top + 0.0165), ink(DOC[doc]), g, bevel=0.001)
        text(f"{chunk_id}_tabtext", chunk_id, 0.017, (tab_x, -0.0025, top + 0.0165), ink((255, 255, 255)), g, rot=(math.radians(90), 0, 0))
        strip(f"{chunk_id}_vec", g, (-(IW - 0.04) / 2 + 0.015, -0.002, top - 0.03), n=22, seed=100 + i, count_label="", rot=(math.radians(90), 0, 0))
    return root
