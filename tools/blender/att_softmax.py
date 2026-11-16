"""Attention stage 6, Softmax: each row of scores becomes shares that add up to 100%.

Six rows, one per word. Each row is a bar split into shares, one colour per word it looks at. Real weights
(average of the two heads, no mask). Every bar is the same length: 100%.
"""

import numpy as np

from blib import box, empty, ink, plastic, text, wedge
from colors import INK
from shapes import PALETTE8, data, nameplate


def build():
    d = data("attention")
    root = empty("softmax")
    top = wedge("slope", 1.2, 0.7, 30, root)
    words = d["tokens"]
    w = np.array(d["weights_mean"])
    colour = {}
    for t in words:
        colour.setdefault(t, PALETTE8[len(colour)])
    L = 0.8
    for r in range(6):
        g = empty(f"row{r}", (0, (2.5 - r) * 0.1, 0.003), top, explode=(0.0, 0.0, 0.02 * r))
        x = -L / 2
        for c in range(6):
            wd = L * w[r, c]
            if wd < 0.001:
                continue
            box(f"s{c}", (wd - 0.004, 0.07, 0.03), (x + wd / 2, 0, 0.015), plastic(colour[words[c]]), g, bevel=0.004)
            if wd > 0.07:
                text(f"p{c}", f"{round(100 * w[r, c])}", 0.032, (x + wd / 2, 0, 0.0315), ink((255, 255, 255)), g)
            x += wd
        text("who", words[r], 0.04, (-L / 2 - 0.05, 0, 0.01), ink(INK), g, align="RIGHT")
    nameplate("lbl", "each row = 100%", top, (0, -0.3, 0.006), 0.4, 0.05, 0.034)
    return root
