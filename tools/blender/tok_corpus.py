"""Tokenization stage 1, Training corpus: the lighthouse keeper's log, with a lighthouse beside it.

The open logbook shows the corpus's real opening lines. The corpus is 1045 characters long.
"""

import math

from blib import box, cylinder, empty, ink, material, paper, text, text_lines
from colors import CARD, GREY, INK
from shapes import AMBER, BRASS, RED, brass, cone, data, led

LOG = ["The keeper lit the lantern", "at dusk. The tide was low and", "the wind came from the west."]


def build():
    root = empty("training_corpus")
    cloth = material("cloth", (36, 78, 62), rough=0.9)
    book = empty("book", (-0.18, 0, 0.0), root)
    book.rotation_euler = (0, 0, math.radians(8))
    box("cover", (0.78, 0.5, 0.03), (0, 0, 0.015), cloth, book, bevel=0.01)
    for s in (-1, 1):
        box(f"pages{s}", (0.36, 0.45, 0.05), (s * 0.19, 0, 0.055), paper(CARD), book, bevel=0.004)
    box("spine", (0.02, 0.5, 0.045), (0, 0, 0.05), cloth, book)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(f"corner{sx}{sy}", (0.05, 0.05, 0.034), (sx * 0.37, sy * 0.22, 0.015), brass(), book, bevel=0.006)
    text("book_title", "KEEPER'S LOG", 0.03, (0.19, 0.18, 0.0815), ink(INK), book)
    text_lines("ruled", (-0.34, 0.1), [0.3, 0.28, 0.3, 0.25, 0.29, 0.22, 0.3, 0.2], 0.045, 0.004, ink((200, 205, 215)), book, z=0.0805)
    for i, ln in enumerate(LOG):
        text(f"entry{i}", ln, 0.026, (0.03, 0.1 - i * 0.045, 0.0815), ink(INK), book, align="LEFT")
    box("ribbon", (0.012, 0.3, 0.003), (0.19, -0.3, 0.062), ink((180, 50, 60)), book)
    text("size_tag", "1045 characters", 0.028, (0.19, -0.14, 0.0815), ink(INK), book)
    # A small lighthouse: striped tower, gallery, glowing lamp, red roof.
    lh = empty("lighthouse", (0.3, 0.02, 0.0), root, explode=(0.06, 0.04, 0.0))
    stripe = [paper((248, 246, 240)), ink(RED)]
    h = 0.07
    for i in range(5):
        r1, r2 = 0.085 - i * 0.012, 0.085 - (i + 1) * 0.012
        cone(f"tower{i}", r1, r2, h, (0, 0, h * (i + 0.5)), stripe[i % 2], lh)
    cylinder("gallery", 0.065, 0.012, (0, 0, h * 5 + 0.006), ink((60, 64, 74)), lh)
    cylinder("lamp", 0.038, 0.05, (0, 0, h * 5 + 0.037), led(AMBER, 6.0), lh)
    cone("roof", 0.055, 0.0, 0.05, (0, 0, h * 5 + 0.087), ink(RED), lh)
    return root
