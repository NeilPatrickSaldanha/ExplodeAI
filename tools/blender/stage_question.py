"""The learner's question, as a speech bubble. Scenery, not a pipeline stage."""

import math

from blib import box, empty, ink, paper, text
from colors import CARD, INK, QUERY


def build():
    root = empty("question")
    g = empty("bubble", (0, 0, 0.11), root)
    g.rotation_euler = (math.radians(70), 0, 0)
    box("rim", (0.5, 0.17, 0.004), (0, 0, -0.002), ink(QUERY), g, bevel=0.012)
    box("face", (0.484, 0.154, 0.004), (0, 0, 0.0008), paper(CARD), g, bevel=0.009)
    tail = box("tail", (0.05, 0.05, 0.004), (-0.17, -0.085, -0.002), ink(QUERY), g)
    tail.rotation_euler = (0, 0, math.radians(45))
    text("line1", "How long do I have", 0.03, (0, 0.025, 0.004), ink(INK), g)
    text("line2", "to return a bike?", 0.03, (0, -0.025, 0.004), ink(INK), g)
    return root
