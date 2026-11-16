"""Tokenization stage 3, Base alphabet: all 256 bytes, as a letterpress type case.

16 x 16 compartments, one per byte value (columns 0-F, rows 0-F). The printable characters carry their
letter; the other byte values are blank. These 256 symbols can spell any text.
"""

from blib import box, empty, ink, material, text, wedge
from colors import INK
from shapes import MAPLE, WALNUT, brass, wood

N = 16
CELL = 0.05


def build():
    root = empty("base_alphabet")
    top = wedge("slope", N * CELL + 0.12, N * CELL + 0.12, 34, root)
    box("frame", (N * CELL + 0.04, N * CELL + 0.04, 0.02), (0, 0, 0.01), wood(WALNUT), top, bevel=0.008)
    for row in range(N):
        for col in range(N):
            b = row * N + col
            x = (col - (N - 1) / 2) * CELL
            y = ((N - 1) / 2 - row) * CELL
            printable = 32 < b < 127
            box(f"c{b}", (CELL - 0.006, CELL - 0.006, 0.006), (x, y, 0.022), wood(MAPLE if printable else (170, 140, 100)), top, bevel=0.0015)
            if printable:
                text(f"g{b}", chr(b), CELL * 0.62, (x, y, 0.0258), ink((236, 238, 244)), top)
    for i in range(N):
        h = f"{i:X}"
        text(f"col{i}", h, 0.03, ((i - (N - 1) / 2) * CELL, N * CELL / 2 + 0.045, 0.01), ink((236, 238, 244)), top)
        text(f"row{i}", h, 0.03, (-N * CELL / 2 - 0.045, ((N - 1) / 2 - i) * CELL, 0.01), ink((236, 238, 244)), top)
    box("plate", (0.36, 0.06, 0.006), (0, -N * CELL / 2 - 0.07, 0.012), brass(), top, bevel=0.004)
    text("plate_t", "256 bytes", 0.035, (0, -N * CELL / 2 - 0.07, 0.0165), ink((30, 28, 20)), top)
    return root
