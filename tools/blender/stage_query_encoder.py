"""Stage 5, Question fingerprint maker: the question becomes a vector of the same kind (1024 numbers).

The question card is pink, the colour used for the question everywhere. Its strip has a pink frame,
but the tiles are the same kind as the chunks' tiles, which is what makes them comparable.
"""

from blib import box, empty, ink, paper, text, wedge
from colors import CARD, INK, QUERY
from vector import strip


def build():
    root = empty("question_fingerprint_maker")
    top = wedge("slope", 0.72, 0.3, 36, root)
    g = empty("question_card", (-0.2, 0.0, 0.003), top)
    box("q_stock", (0.3, 0.17, 0.003), (0, 0, 0), paper(CARD), g, bevel=0.0008)
    box("q_stripe", (0.3, 0.042, 0.0008), (0, 0.064, 0.0019), ink(QUERY), g)
    text("q_label", "your question", 0.026, (-0.138, 0.064, 0.0023), ink((255, 255, 255)), g, align="LEFT")
    text("q_line1", "How long do I have", 0.024, (-0.138, 0.012, 0.0021), ink(INK), g, align="LEFT")
    text("q_line2", "to return a bike?", 0.024, (-0.138, -0.03, 0.0021), ink(INK), g, align="LEFT")
    strip("q_vec", top, (-0.04, 0.02, 0.004), seed=7, frame=(248, 214, 230), count_label="1024 numbers", explode=(0.08, 0, 0))
    return root
