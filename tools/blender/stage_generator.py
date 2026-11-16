"""Stage 8, Writer: the answer, built from sentences on the page, each tagged with the chunk it came from.

These are the two real sentences the lesson's simple helper quotes for the default question.
"""

import math

from blib import box, cylinder, empty, ink, material, paper, text
from colors import CARD, DOC, GREY, HIGHLIGHT, INK

LINES = [
    ("Ridgeline Bikes accepts returns of unused", True),
    ("bikes within 30 days of delivery.", True),
    ("Returned bikes must include the original", True),
    ("packaging.", True),
]
TAG_AFTER = {1, 3}  # a source tag follows the last line of each sentence


def build():
    root = empty("writer")
    sheet = empty("answer_sheet", (-0.04, 0, 0.03), root)
    sheet.rotation_euler = (math.radians(22), 0, 0)
    W, D = 0.56, 0.38
    box("sheet", (W, D, 0.003), (0, 0, 0), paper(CARD), sheet, bevel=0.0006)
    text("title", "Answer", 0.024, (-W / 2 + 0.03, D / 2 - 0.04, 0.002), ink(INK), sheet, align="LEFT")
    text("note", "quoted from the page", 0.014, (-W / 2 + 0.135, D / 2 - 0.04, 0.002), ink(GREY), sheet, align="LEFT")
    hl = material("highlighter", HIGHLIGHT, rough=0.7)
    for i, (line, _) in enumerate(LINES):
        y = D / 2 - 0.1 - i * 0.05
        width = 0.0092 * len(line)
        box(f"hl{i}", (width + 0.012, 0.03, 0.0008), (-W / 2 + 0.024 + width / 2, y, 0.0017), hl, sheet)
        text(f"line{i}", line, 0.018, (-W / 2 + 0.03, y, 0.0022), ink(INK), sheet, align="LEFT")
        if i in TAG_AFTER:
            tag = empty(f"source_{i}", (-W / 2 + 0.05 + width + 0.06, y, 0.0024), sheet, explode=(0, 0.02, 0.015))
            box(f"tag{i}", (0.1, 0.026, 0.002), (0, 0, 0), ink(DOC["returns"]), tag, bevel=0.003)
            text(f"tagtext{i}", "returns#0", 0.014, (0, 0, 0.0016), ink((255, 255, 255)), tag)
    # A pen resting across the corner of the sheet.
    pen = empty("pen", (0.2, -0.1, 0.045), root, explode=(0.06, 0.06, 0.04))
    pen.rotation_euler = (math.radians(8), math.radians(90), math.radians(-35))
    body = material("pen_body", (30, 42, 72), rough=0.25, coat=0.8)
    steel = material("steel", (205, 209, 216), rough=0.22, metal=1.0)
    cylinder("pen_barrel", 0.011, 0.24, (0, 0, 0), body, pen)
    cylinder("pen_band", 0.0115, 0.012, (0, 0, 0.05), steel, pen)
    cylinder("pen_tip", 0.006, 0.03, (0, 0, -0.135), steel, pen, verts=24)
    return root
