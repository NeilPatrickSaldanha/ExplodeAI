"""Embeddings stage 2, Your text: you type a sentence; it appears on the display ("a place to put my books")."""

from blib import box, empty, ink, plastic
from colors import INK
from shapes import data, led_panel


def build():
    d = data("embeddings")
    root = empty("your_text")
    led_panel("display", ["a place to put", "my books"], root, (0, -0.02, 0.36), w=0.8, h=0.3, size=0.085, rot=(1.25, 0, 0))
    box("post", (0.06, 0.05, 0.28), (0, 0.1, 0.14), ink((70, 76, 90)), root, bevel=0.01)
    box("kbd", (0.78, 0.26, 0.03), (0, -0.28, 0.015), ink((52, 56, 68)), root, bevel=0.012)
    keys = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    for r, row in enumerate(keys):
        for i, ch in enumerate(row):
            x = (i - (len(row) - 1) / 2) * 0.066
            box(f"k{r}{i}", (0.054, 0.05, 0.016), (x, -0.2 - r * 0.058, 0.038), plastic((236, 238, 244)), root, bevel=0.006)
    box("space", (0.36, 0.05, 0.016), (0, -0.2 - 3 * 0.058, 0.038), plastic((236, 238, 244)), root, bevel=0.006)
    return root
