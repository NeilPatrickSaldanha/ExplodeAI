"""Stage 3, Fingerprint maker: each chunk gets a vector, a fixed-length list of numbers (1024 here).

Shown for three chunks: the card on the left, its vector strip sliding out to the right.
"""

import math

from blib import empty
from cards import card
from vector import strip

SHOWN = [("returns#0", 11), ("battery#1", 22), ("warranty#0", 33)]


def build():
    root = empty("fingerprint_maker")
    tilt = math.radians(55)
    for i, (chunk_id, seed) in enumerate(SHOWN):
        y = 0.16 - i * 0.16
        z = 0.06 + (len(SHOWN) - 1 - i) * 0.03
        card(chunk_id, root, (-0.25, y, z), lines=3, w=0.17, h=0.11)
        strip(f"vec_{chunk_id}", root, (-0.155, y, z + 0.004), n=16, seed=seed, rot=(tilt, 0, 0),
              count_label="1024 numbers" if i == len(SHOWN) - 1 else "", explode=(0.09, 0, 0))
    return root
