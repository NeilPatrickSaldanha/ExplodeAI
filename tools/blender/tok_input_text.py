"""Tokenization stage 6, Input text: the new sentence on a glowing display, with its length: 35 bytes."""

from blib import box, empty, ink, text
from colors import INK
from shapes import AMBER, data, led_panel, nameplate


def build():
    d = data("tokenization")
    root = empty("input_text")
    panel = led_panel("display", ["The keeper lit", "the lantern at dusk."], root, (0, 0, 0.3), w=0.86, h=0.3, size=0.085, rot=(1.18, 0, 0))
    box("post", (0.07, 0.06, 0.3), (0, 0.06, 0.15), ink((70, 76, 90)), root, bevel=0.01)
    nameplate("size", "35 bytes", root, (0, -0.12, 0.016), 0.34, 0.055, 0.036, rot=(1.1, 0, 0))
    return root
