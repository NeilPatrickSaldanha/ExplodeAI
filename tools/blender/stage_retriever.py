"""Stage 6, Card finder: every chunk scored against the question and ranked; the top 3 are kept.

The scores and the order are the real ones from a default run (dense ranking, default embedder).
The bar length is the score. The one negative score (battery#0) runs the other way, in orange.
"""

import math

from blib import box, empty, ink, material, paper, text
from colors import CARD, DOC, GOLD, GREY, INK, NEG, POS, QUERY
from vector import strip

RANKING = [
    ("returns#0", 0.1168), ("battery#1", 0.0707), ("returns#1", 0.0669), ("service#1", 0.061),
    ("warranty#0", 0.0349), ("service#0", 0.0259), ("shipping#0", 0.025), ("warranty#1", 0.0),
    ("sizing#0", 0.0), ("sizing#1", 0.0), ("battery#0", -0.0887),
]
KEPT = 3
BW, BD = 0.74, 0.64  # board width and depth
ROW = 0.042
BAR_MAX = 0.17  # bar length for the top score


def build():
    root = empty("card_finder")
    board = empty("board", (0, 0, 0.02), root)
    board.rotation_euler = (math.radians(24), 0, 0)
    box("tray", (BW, BD, 0.012), (0, 0, -0.006), material("tray", (226, 230, 236), rough=0.4, coat=0.2), board, bevel=0.006)
    top = BD / 2 - 0.05
    text("q_label", "compared with your question:", 0.016, (-BW / 2 + 0.03, top, 0.002), ink(QUERY), board, align="LEFT")
    strip("q_vec", board, (0.1, top, 0.0), n=10, seed=7, frame=(248, 214, 230), count_label="")
    zero_x = 0.06
    y0 = top - 0.06
    for i, (chunk_id, score) in enumerate(RANKING):
        kept = i < KEPT
        y = y0 - i * ROW - (0.022 if not kept else 0.0)
        lift = (0, 0.05, 0.03) if kept else None
        row = empty(f"row_{chunk_id}", (0, y, 0.004 if kept else 0.0), board, explode=lift)
        face = CARD if kept else (236, 238, 241)
        box(f"{chunk_id}_rowbg", (BW - 0.04, ROW - 0.006, 0.004), (0, 0, 0), paper(face), row, bevel=0.002)
        badge = GOLD if kept else GREY
        box(f"{chunk_id}_rank", (0.03, 0.026, 0.004), (-BW / 2 + 0.04, 0, 0.003), ink(badge), row, bevel=0.003)
        text(f"{chunk_id}_ranktext", str(i + 1), 0.016, (-BW / 2 + 0.04, 0, 0.0055), ink(INK if kept else (255, 255, 255)), row)
        doc = chunk_id.split("#")[0]
        box(f"{chunk_id}_tab", (0.11, 0.024, 0.003), (-BW / 2 + 0.12, 0, 0.003), ink(DOC[doc]), row, bevel=0.002)
        text(f"{chunk_id}_id", chunk_id, 0.014, (-BW / 2 + 0.12, 0, 0.0052), ink((255, 255, 255)), row)
        length = abs(score) / RANKING[0][1] * BAR_MAX
        if length > 0.001:
            colour = POS if score > 0 else NEG
            x = zero_x + length / 2 if score > 0 else zero_x - length / 2
            box(f"{chunk_id}_bar", (length, 0.016, 0.006), (x, 0, 0.004), material("bar", colour, rough=0.35, coat=0.4), row, bevel=0.002)
        text(f"{chunk_id}_score", f"{score:.3f}", 0.014, (BW / 2 - 0.03, 0, 0.0045), ink(INK), row, align="RIGHT")
    box("zero_line", (0.002, ROW * len(RANKING) + 0.03, 0.002), (zero_x, y0 - ROW * (len(RANKING) - 1) / 2 - 0.011, 0.006), ink(GREY), board)
    # A gold bracket marks the cut-off: only the top 3 are kept.
    cut_y = y0 - (KEPT - 0.5) * ROW - 0.011
    box("cutoff", (BW - 0.02, 0.004, 0.004), (0, cut_y + 0.008, 0.008), ink(GOLD), board)
    box("cutoff_plate", (0.13, 0.022, 0.003), (-BW / 2 + 0.09, cut_y - 0.006, 0.006), ink(GOLD), board, bevel=0.003)
    text("cutoff_label", "kept: top 3", 0.014, (-BW / 2 + 0.09, cut_y - 0.006, 0.0085), ink(INK), board)
    return root
