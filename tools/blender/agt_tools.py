"""Agents stage 2, Tool registry: the four tools on a pegboard.

search_help_centre (magnifier), get_order (parcel), days_between (calendar), issue_refund (banknote, with an
orange "needs approval" tag: it changes something). Names and descriptions are the real tool list.
"""

from blib import box, cylinder, empty, ink, material, plastic, text
from colors import INK
from shapes import BLACK, brass, data, nameplate, steel, torus, wood, MAPLE


def build():
    d = data("agents")
    root = empty("tool_registry")
    box("board", (1.0, 0.05, 0.62), (0, 0.025, 0.33), wood((205, 190, 160)), root, bevel=0.012)
    for r in range(6):
        for c in range(10):
            cylinder(f"h{r}{c}", 0.006, 0.01, (-0.45 + c * 0.1, 0.0, 0.07 + r * 0.1), ink((120, 110, 90)), root, rot=(1.5708, 0, 0), verts=8)
    slots = [(-0.36, "search_help_centre"), (-0.12, "get_order"), (0.12, "days_between"), (0.36, "issue_refund")]
    for i, (x, name) in enumerate(slots):
        g = empty(f"tool{i}", (x, -0.02, 0.38), root, explode=(0, -0.05, 0.0))
        box("card", (0.21, 0.014, 0.3), (0, 0, 0), material("card", (250, 247, 238), rough=0.5), g, bevel=0.006)
        # icon
        ic = empty("icon", (0, -0.012, 0.05), g)
        if i == 0:
            torus("rim", 0.045, 0.01, (0, 0, 0), steel(), ic, rot=(1.5708, 0, 0))
            cylinder("hd", 0.009, 0.06, (0.05, 0, -0.05), brass(), ic, rot=(0, 0.785, 0))
        elif i == 1:
            box("pk", (0.1, 0.06, 0.08), (0, 0, 0), plastic((190, 140, 90)), ic, bevel=0.006)
            box("tp", (0.012, 0.062, 0.082), (0, 0, 0), ink((230, 220, 200)), ic)
        elif i == 2:
            box("cal", (0.1, 0.012, 0.09), (0, 0, 0), plastic((250, 250, 250)), ic, bevel=0.006)
            box("top", (0.1, 0.014, 0.025), (0, -0.002, 0.034), plastic((214, 69, 62)), ic, bevel=0.004)
            text("d", "16", 0.04, (0, -0.0095, -0.005), ink(INK), ic, rot=(1.5708, 0, 0))
        else:
            box("note", (0.12, 0.008, 0.06), (0, 0, 0), plastic((120, 190, 140)), ic, bevel=0.004)
            cylinder("coin", 0.02, 0.006, (0, -0.007, 0), brass(), ic, rot=(1.5708, 0, 0))
        text("nm", name, 0.021, (0, -0.009, -0.06), ink(INK), g, rot=(1.5708, 0, 0))
        if i == 3:
            box("tag", (0.19, 0.01, 0.05), (0, -0.012, -0.115), ink((226, 120, 40)), g, bevel=0.004)
            text("ap", "needs approval", 0.022, (0, -0.0185, -0.115), ink((255, 255, 255)), g, rot=(1.5708, 0, 0))
    return root
