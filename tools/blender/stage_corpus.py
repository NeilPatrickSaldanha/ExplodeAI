"""Stage 1, Help articles: the six real help-centre articles as printed sheets, one colour each."""

import math

from blib import box, empty, ink, paper, text, text_lines
from colors import CARD, DOC, GREY

ARTICLES = [
    ("service", "Tune-ups and service"),
    ("sizing", "Frame sizing guide"),
    ("shipping", "Shipping and assembly"),
    ("battery", "E-Trail battery care"),
    ("warranty", "Warranty coverage"),
    ("returns", "Returns and refunds"),
]

W, H = 0.40, 0.36  # sheet width (x) and length (y)


def sheet(doc_id, title, parent, loc, rot_z, explode):
    g = empty(f"sheet_{doc_id}", loc, parent, explode)
    g.rotation_euler = (0, 0, rot_z)
    box(f"{doc_id}_paper", (W, H, 0.003), (0, 0, 0), paper(CARD), g, bevel=0.0006)
    band = DOC[doc_id]
    box(f"{doc_id}_band", (W, 0.075, 0.001), (0, H / 2 - 0.0375, 0.002), ink(band), g)
    text(f"{doc_id}_title", title, 0.022, (0, H / 2 - 0.0375, 0.0028), ink((255, 255, 255)), g)
    widths = [0.27, 0.29, 0.25, 0.28, 0.22, 0.27, 0.26, 0.18]
    text_lines(f"{doc_id}_l", (-W / 2 + 0.025, H / 2 - 0.11), widths, 0.034, 0.008, ink(GREY), g, z=0.0019)
    return g


def build():
    root = empty("help_articles")
    stack = empty("stack", (0, 0, 0.0), root)
    stack.rotation_euler = (math.radians(14), 0, 0)
    for i, (doc_id, title) in enumerate(ARTICLES):
        k = i - 2.5
        # Each sheet sits lower and nearer than the one behind it, so every title band stays visible.
        loc = (k * 0.03, 0.21 - i * 0.082, 0.02 + i * 0.006)
        sheet(doc_id, title, stack, loc, math.radians(-k * 1.2), explode=(k * 0.05, i * 0.04, i * 0.05))
    return root
