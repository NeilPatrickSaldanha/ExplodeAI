"""The index card used for one chunk, shared by every stage that shows chunks."""

import math

from blib import box, empty, ink, paper, text, text_lines
from colors import CARD, DOC, GREY, INK

# The 11 chunks of a default run (sentence chunking, up to 40 words), with their real word counts.
CHUNKS = [
    ("returns#0", 36), ("returns#1", 5), ("warranty#0", 36), ("warranty#1", 17),
    ("battery#0", 25), ("battery#1", 25), ("shipping#0", 37), ("sizing#0", 33),
    ("sizing#1", 14), ("service#0", 33), ("service#1", 10),
]
WORDS = dict(CHUNKS)
CW, CH = 0.22, 0.13  # card width and height


def card(chunk_id, parent, loc, tilt=55, explode=None, lines=None, w=CW, h=CH):
    """An index card standing tilted towards the viewer. Its stripe is the colour of its source article."""
    g = empty(f"card_{chunk_id}", loc, parent, explode)
    g.rotation_euler = (math.radians(tilt), 0, 0)
    doc = chunk_id.split("#")[0]
    box(f"{chunk_id}_stock", (w, h, 0.003), (0, 0, 0), paper(CARD), g, bevel=0.0008)
    box(f"{chunk_id}_stripe", (w, 0.042, 0.0008), (0, h / 2 - 0.021, 0.0019), ink(DOC[doc]), g)
    text(f"{chunk_id}_id", chunk_id, 0.028, (-w / 2 + 0.012, h / 2 - 0.021, 0.0023), ink((255, 255, 255)), g, align="LEFT")
    n = lines if lines is not None else max(1, math.ceil(WORDS.get(chunk_id, 10) / 10))
    widths = [w * 0.78 if i < n - 1 else w * 0.45 for i in range(n)]
    text_lines(f"{chunk_id}_l", (-w / 2 + 0.012, h / 2 - 0.058), widths, 0.0165, 0.006, ink(GREY), g, z=0.0019)
    return g
