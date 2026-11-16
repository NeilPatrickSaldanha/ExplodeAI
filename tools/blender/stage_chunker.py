"""Stage 2, Card cutter: the six articles cut into the 11 real chunks of a default run.

Each card carries its chunk id, its source article's colour, and one text line per ten words, so a
36-word chunk is visibly fuller than a 5-word one. The cards lie on a sloped board facing the viewer.
"""

from blib import empty, wedge
from cards import CHUNKS, CW, card

ROWS = [
    ["returns#0", "returns#1", "warranty#0", "warranty#1"],
    ["battery#0", "battery#1", "shipping#0", "sizing#0"],
    ["sizing#1", "service#0", "service#1"],
]


def build():
    root = empty("card_cutter")
    assert sum(len(r) for r in ROWS) == len(CHUNKS)
    top = wedge("slope", 4 * (CW + 0.025) + 0.04, 0.5, 36, root)
    for r, row in enumerate(ROWS):
        for c, chunk_id in enumerate(row):
            k = c - (len(row) - 1) / 2
            card(chunk_id, top, (k * (CW + 0.025), 0.155 - r * 0.155, 0.003), tilt=0, explode=(k * 0.05, 0.03, r * 0.03))
    return root
