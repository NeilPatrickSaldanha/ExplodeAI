"""Agents stage 1, Goal: the customer's message, on a phone.

A chat bubble on a phone screen: "Hi! I'd like to return my E-Trail from order 1001. Can I get a refund?"
"""

import math

from blib import box, cylinder, empty, ink, material, text
from colors import INK
from shapes import BLACK, data, led_panel, nameplate


def build():
    d = data("agents")
    root = empty("goal")
    ph = empty("phone", (0, 0, 0.0), root)
    ph.rotation_euler = (-0.35, 0, 0)
    box("body", (0.34, 0.62, 0.035), (0, 0, 0.3), material("phone", (30, 34, 44), rough=0.3, metal=0.6), ph, bevel=0.02).rotation_euler = (1.5708, 0, 0)
    ph.location = (0, 0, 0)
    screen = empty("screen", (0, -0.0185, 0.3), ph)
    screen.rotation_euler = (1.5708, 0, 0)
    box("glass", (0.3, 0.58, 0.004), (0, 0, 0), material("scr", (232, 238, 248), rough=0.2, coat=0.4), screen, bevel=0.01)
    box("bar", (0.3, 0.05, 0.005), (0, 0.265, 0.003), ink((60, 140, 220)), screen)
    text("hdr", "Ridgeline Bikes", 0.032, (0, 0.265, 0.0065), ink((255, 255, 255)), screen)
    box("bubble", (0.24, 0.26, 0.006), (-0.01, 0.07, 0.004), ink((210, 232, 255)), screen, bevel=0.03)
    lines = ["Hi! I'd like to", "return my E-Trail", "from order 1001.", "Can I get a", "refund?"]
    for i, ln in enumerate(lines):
        text(f"l{i}", ln, 0.03, (-0.105, 0.17 - i * 0.045, 0.0075), ink(INK), screen, align="LEFT")
    box("reply", (0.16, 0.05, 0.006), (0.06, -0.12, 0.004), ink((225, 228, 236)), screen, bevel=0.02)
    text("dots", "...", 0.04, (0.06, -0.125, 0.0075), ink(INK), screen)
    nameplate("lbl", "customer message", root, (0, -0.2, 0.012), 0.42, 0.055, 0.034, rot=(1.1, 0, 0))
    return root
