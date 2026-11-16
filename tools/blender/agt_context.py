"""Agents stage 7, Context: the case file grows every step; the whole pile is read again each time.

One column per step, height = tokens read at that step (1475, 1955, 2203, 2526, 2799: real counts from a
default run, counted with this site's small teaching tokenizer).
"""

from blib import box, empty, ink, plastic, text, wedge
from colors import INK
from shapes import data, nameplate


def build():
    d = data("agents")
    root = empty("context")
    top = wedge("slope", 1.1, 0.6, 30, root)
    steps = d["steps"]
    H = 0.45
    top_t = max(s["tokens_in"] for s in steps)
    for i, s in enumerate(steps):
        x = (i - 2) * 0.2
        h = H * s["tokens_in"] / top_t
        g = empty(f"step{i}", (x, 0.0, 0.003), top, explode=(0, 0, 0.03))
        # the column is a stack of folders: each new step adds a sheet on top of the last
        layers = 4 + i
        for k in range(layers):
            lh = h / layers
            col = (47, 111, 214) if k == layers - 1 else (170, 190, 225)
            box(f"f{k}", (0.15, 0.12, lh - 0.004), (0, 0, lh * (k + 0.5)), plastic(col), g, bevel=0.004)
        text("n", f"{s['tokens_in']:,}", 0.034, (0, -0.1, 0.006), ink((236, 238, 244)), top).location.x = x
        text("s", f"step {s['index']}", 0.03, (0, -0.15, 0.006), ink((236, 238, 244)), top).location.x = x
    nameplate("lbl", "tokens read, step by step", top, (0, 0.24, 0.004), 0.5, 0.05, 0.03)
    return root
