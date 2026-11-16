"""Agents stage 6, Result: what the tool sent back, as a slip in the inbox.

The order lookup's result (E-Trail electric bike, 2,899, delivered 2026-10-05) comes back as a message that
names the call it answers. A warning flag marks the risk: a result can hide instructions the model might obey.
"""

from blib import box, empty, ink, material, plastic, text, wedge
from colors import INK
from shapes import nameplate, steel


def build():
    root = empty("observe")
    top = wedge("slope", 1.1, 0.6, 28, root)
    tray = empty("inbox", (-0.15, 0.0, 0.003), top)
    box("floor", (0.6, 0.4, 0.02), (0, 0, 0.01), steel(), tray, bevel=0.008)
    box("back", (0.6, 0.015, 0.1), (0, 0.19, 0.06), steel(), tray, bevel=0.006)
    for s in (-1, 1):
        box(f"side{s}", (0.015, 0.4, 0.07), (s * 0.295, 0, 0.045), steel(), tray, bevel=0.006)
    slip = empty("slip", (0, 0.0, 0.03), tray, explode=(0, 0.0, 0.06))
    slip.rotation_euler = (-0.2, 0, 0)
    box("p", (0.5, 0.32, 0.006), (0, 0, 0.003), material("slip", (250, 247, 238), rough=0.85), slip, bevel=0.002)
    box("hd", (0.5, 0.05, 0.007), (0, 0.135, 0.0035), ink((47, 111, 214)), slip)
    text("a", "result of get_order", 0.03, (0, 0.135, 0.0075), ink((255, 255, 255)), slip)
    for i, ln in enumerate(["E-Trail electric bike", "price 2899", "delivered 2026-10-05"]):
        text(f"l{i}", ln, 0.035, (-0.22, 0.05 - i * 0.065, 0.0065), ink(INK), slip, align="LEFT")
    flag = empty("flag", (0.35, 0.1, 0.003), top, explode=(0.04, 0, 0.04))
    box("pole", (0.012, 0.012, 0.3), (0, 0, 0.15), steel(), flag)
    box("cloth", (0.16, 0.012, 0.1), (0.09, 0, 0.26), plastic((226, 120, 40)), flag, bevel=0.004)
    text("w", "!", 0.07, (0.09, -0.008, 0.26), ink((255, 255, 255)), flag, rot=(1.5708, 0, 0))
    nameplate("lbl", "text the model reads", top, (0.38, -0.12, 0.004), 0.36, 0.05, 0.03)
    return root
