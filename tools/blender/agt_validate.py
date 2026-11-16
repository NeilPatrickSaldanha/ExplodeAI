"""Agents stage 4, Check: a checkpoint that only lets a correctly shaped order id through.

The rule is "an A followed by four digits". "1001" is rejected at the gate (red cross); "A1001" passes (green
tick). The same two ids as the lesson's Return example.
"""

from blib import box, cylinder, empty, ink, plastic, text, wedge
from colors import INK
from shapes import BLACK, check_seal, nameplate, steel


def build():
    root = empty("validate")
    top = wedge("slope", 1.2, 0.6, 28, root)
    # the gate
    for s in (-1, 1):
        box(f"post{s}", (0.05, 0.05, 0.34), (s * 0.2, 0.0, 0.17), steel(), top, bevel=0.01)
    box("beam", (0.5, 0.05, 0.05), (0, 0, 0.34), steel(), top, bevel=0.01)
    box("slot_label", (0.3, 0.012, 0.07), (0, -0.032, 0.29), plastic((250, 247, 238)), top, bevel=0.004)
    text("rule", "A + 4 digits", 0.04, (0, -0.04, 0.29), ink(INK), top, rot=(1.5708, 0, 0))
    # rejected id (left) and accepted id (right)
    bad = empty("bad", (-0.45, -0.15, 0.003), top, explode=(-0.04, 0, 0.02))
    box("t", (0.2, 0.09, 0.04), (0, 0, 0.02), plastic((236, 238, 244)), bad, bevel=0.008)
    text("id", "1001", 0.06, (0, 0, 0.0415), ink(INK), bad)
    check_seal("x", bad, (0, -0.15, 0.0), 0.06, False)
    good = empty("good", (0.45, -0.15, 0.003), top, explode=(0.04, 0, 0.02))
    box("t", (0.26, 0.09, 0.04), (0, 0, 0.02), plastic((236, 238, 244)), good, bevel=0.008)
    text("id", "A1001", 0.06, (0, 0, 0.0415), ink(INK), good)
    check_seal("ok", good, (0, -0.15, 0.0), 0.06, True)
    nameplate("lbl", "rejected: must match A1001", top, (-0.4, 0.25, 0.004), 0.5, 0.05, 0.028, face=(214, 69, 62), ink_c=(255, 255, 255))
    nameplate("lbl2", "accepted", top, (0.45, 0.25, 0.004), 0.3, 0.05, 0.03, face=(46, 158, 91), ink_c=(255, 255, 255))
    return root
