"""Stage 3, Fingerprint maker: each chunk gets a vector, a fixed-length list of numbers (1024 here).

Shown for three chunks: the card on the left, its vector strip sliding out to the right.
"""

from blib import empty, wedge
from cards import card
from vector import strip

SHOWN = [("returns#0", 11), ("battery#1", 22), ("warranty#0", 33)]


def build():
    root = empty("fingerprint_maker")
    top = wedge("slope", 0.72, 0.56, 36, root)
    for i, (chunk_id, seed) in enumerate(SHOWN):
        y = 0.17 - i * 0.17
        card(chunk_id, top, (-0.235, y, 0.003), tilt=0, lines=3)
        strip(f"vec_{chunk_id}", top, (-0.12, y + 0.01, 0.004), seed=seed,
              count_label="1024 numbers" if i == len(SHOWN) - 1 else "", explode=(0.08, 0, 0))
    return root
