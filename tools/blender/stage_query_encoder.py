"""Stage 5, Question fingerprint maker: the question becomes a vector of the same kind (1024 numbers).

The question card is pink, the colour used for the question everywhere. Its strip has a pink frame,
but the tiles are the same kind as the chunks' tiles, which is what makes them comparable.
"""

import math

from blib import box, empty, ink, paper, text
from colors import CARD, INK, QUERY
from vector import strip


def build():
    root = empty("question_fingerprint_maker")
    tilt = math.radians(55)
    g = empty("question_card", (-0.2, 0.02, 0.08), root)
    g.rotation_euler = (tilt, 0, 0)
    box("q_stock", (0.26, 0.13, 0.003), (0, 0, 0), paper(CARD), g, bevel=0.0008)
    box("q_stripe", (0.26, 0.016, 0.0008), (0, 0.057, 0.0019), ink(QUERY), g)
    text("q_label", "your question", 0.015, (-0.118, 0.032, 0.0021), ink(QUERY), g, align="LEFT")
    text("q_line1", "How long do I have", 0.019, (-0.118, 0.0, 0.0021), ink(INK), g, align="LEFT")
    text("q_line2", "to return a bike?", 0.019, (-0.118, -0.03, 0.0021), ink(INK), g, align="LEFT")
    strip("q_vec", root, (-0.065, 0.02, 0.084), n=14, seed=7, frame=(248, 214, 230), count_label="1024 numbers",
          rot=(tilt, 0, 0), explode=(0.09, 0, 0))
    return root
