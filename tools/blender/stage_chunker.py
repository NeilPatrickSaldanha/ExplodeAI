"""Stage 2, Card cutter: the six articles cut into the 11 real chunks of a default run.

Each card carries its chunk id, its source article's colour, and one text line per ten words, so a
36-word chunk is visibly bigger than a 5-word one.
"""

from blib import empty
from cards import CHUNKS, card

ROWS = [
    ["returns#0", "returns#1", "warranty#0", "warranty#1"],
    ["battery#0", "battery#1", "shipping#0", "sizing#0"],
    ["sizing#1", "service#0", "service#1"],
]


def build():
    root = empty("card_cutter")
    assert sum(len(r) for r in ROWS) == len(CHUNKS)
    for r, row in enumerate(ROWS):
        for c, chunk_id in enumerate(row):
            x = (c - (len(row) - 1) / 2) * 0.205
            y = 0.19 - r * 0.17
            card(chunk_id, root, (x, y, 0.055 + (2 - r) * 0.035), explode=((c - (len(row) - 1) / 2) * 0.06, 0.02 * (2 - r), r * 0.06))
    return root
