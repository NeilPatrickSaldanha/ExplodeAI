"""Stage 1, Help articles: the six real help-centre articles as printed sheets, one colour each.

The sheets lean on a sloped board so every title faces the viewer.
"""

from blib import box, empty, ink, paper, text, text_lines, wedge
from colors import CARD, DOC, GREY

ARTICLES = [
    ("service", "Tune-ups and service"),
    ("sizing", "Frame sizing guide"),
    ("shipping", "Shipping and assembly"),
    ("battery", "E-Trail battery care"),
    ("warranty", "Warranty coverage"),
    ("returns", "Returns and refunds"),
]

W, H = 0.46, 0.34  # sheet width (x) and length along the slope
BAND = 0.07


def sheet(doc_id, title, parent, loc, explode):
    g = empty(f"sheet_{doc_id}", loc, parent, explode)
    box(f"{doc_id}_paper", (W, H, 0.003), (0, 0, 0), paper(CARD), g, bevel=0.0006)
    box(f"{doc_id}_band", (W, BAND, 0.001), (0, H / 2 - BAND / 2, 0.002), ink(DOC[doc_id]), g)
    text(f"{doc_id}_title", title, 0.034, (0, H / 2 - BAND / 2, 0.0028), ink((255, 255, 255)), g)
    widths = [0.36, 0.38, 0.33, 0.37, 0.3]
    text_lines(f"{doc_id}_l", (-W / 2 + 0.03, H / 2 - BAND - 0.035), widths, 0.04, 0.012, ink(GREY), g, z=0.0019)
    return g


def build():
    root = empty("help_articles")
    top = wedge("slope", W + 0.06, 0.82, 38, root)
    for i, (doc_id, title) in enumerate(ARTICLES):
        # Each sheet sits lower and nearer than the one behind it, so every title band stays visible.
        loc = (0, 0.2 - i * 0.08, 0.002 + i * 0.004)
        sheet(doc_id, title, top, loc, explode=((i - 2.5) * 0.03, i * 0.03, i * 0.04))
    return root
