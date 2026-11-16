"""Agents stage 3, Decide: a signpost with two ways out, and the tool-match bars.

Left sign: ask for one tool. Right sign: give the final answer. In step 1 the stand-in scores each tool by
shared words (search_help_centre 1.00, get_order 0.14, days_between 0.00, issue_refund 0.14) and picks the top.
"""

import math

from blib import box, cylinder, empty, ink, plastic, text, wedge
from colors import INK
from shapes import PALETTE8, arrow, data, nameplate, steel, wood, MAPLE


def sign(root, name, label, color, x, z, ang):
    g = empty(name, (x, 0, z), root, explode=(x * 0.1, 0, 0.02))
    g.rotation_euler = (0, 0, ang)
    box("b", (0.34, 0.025, 0.1), (0, 0, 0), plastic(color), g, bevel=0.012)
    c = box("tip", (0.1, 0.025, 0.1), (0.19 * (1 if ang >= 0 else -1), 0, 0), plastic(color), g, bevel=0.012)
    c.rotation_euler = (0, 0.785, 0)
    text("t", label, 0.03, (-0.05, -0.0145, 0), ink((255, 255, 255)), g, rot=(1.5708, 0, 0))


def build():
    d = data("agents")
    root = empty("decide")
    cylinder("pole", 0.018, 0.5, (0, 0, 0.25), steel(), root, verts=16)
    sign(root, "tool", "ask for a tool", (47, 111, 214), 0.0, 0.42, 0.0)
    sign(root, "answer", "final answer", (46, 158, 91), 0.0, 0.29, 0.0)
    top = wedge("slope", 0.9, 0.4, 30, root)
    top.location = (0.0, -0.3, 0.0)
    scores = d["steps"][0]["scores"]
    for i, s in enumerate(scores):
        y = 0.12 - i * 0.075
        w = max(0.01, 0.4 * s["score"])
        box(f"b{i}", (w, 0.045, 0.014), (-0.1 + w / 2, y, 0.012), ink(PALETTE8[i]), top, bevel=0.004)
        text(f"n{i}", s["tool"], 0.03, (-0.18, y, 0.005), ink((236, 238, 244)), top, align="RIGHT")
        text(f"v{i}", f"{s['score']:.2f}", 0.032, (-0.08 + max(w, 0.01) + 0.06, y, 0.005), ink((236, 238, 244)), top)
    return root
