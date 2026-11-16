"""Agents stage 5, Run: the application does the work; a risky refund waits for a person's approval.

A machine ("the back office") with an output tray. The refund crate is padlocked and tagged "waiting for a
person to approve", and a big green button is what a person presses.
"""

from blib import box, cylinder, empty, ink, material, plastic, text, wedge
from colors import INK
from shapes import BRASS, brass, check_seal, nameplate, steel, torus, sphere


def build():
    root = empty("execute")
    top = wedge("slope", 1.2, 0.6, 28, root)
    m = empty("machine", (-0.32, 0.05, 0.003), top, explode=(-0.04, 0, 0.0))
    box("body", (0.42, 0.28, 0.24), (0, 0, 0.12), plastic((196, 204, 216)), m, bevel=0.02)
    box("panel", (0.3, 0.012, 0.1), (0, -0.146, 0.16), plastic((40, 44, 56)), m, bevel=0.006)
    for k in range(3):
        sphere(f"led{k}", 0.012, (-0.08 + k * 0.08, -0.155, 0.16), material("l", (80, 220, 120), rough=0.3, emit=3.0), m, 10)
    box("tray", (0.34, 0.1, 0.02), (0, -0.19, 0.03), steel(), m, bevel=0.006)
    text("name", "app does the work", 0.03, (0, -0.146, 0.07), ink(INK), m, rot=(1.5708, 0, 0))
    crate = empty("crate", (0.2, 0.08, 0.003), top, explode=(0.05, 0.0, 0.03))
    box("c", (0.3, 0.22, 0.14), (0, 0, 0.07), plastic((190, 140, 90)), crate, bevel=0.01)
    box("band", (0.31, 0.04, 0.142), (0, 0, 0.071), ink((120, 80, 50)), crate)
    torus("lock", 0.03, 0.008, (0, -0.115, 0.1), brass(), crate, rot=(1.5708, 0, 0))
    box("lockbody", (0.07, 0.025, 0.05), (0, -0.115, 0.07), brass(), crate, bevel=0.006)
    text("rf", "refund", 0.04, (0, -0.116, 0.022), ink((255, 255, 255)), crate, rot=(1.5708, 0, 0))
    nameplate("wait", "waiting for a person to approve", top, (0.2, -0.12, 0.004), 0.5, 0.055, 0.03, face=(226, 120, 40), ink_c=(255, 255, 255))
    btn = empty("button", (0.42, -0.22, 0.003), top, explode=(0.03, 0, 0.03))
    cylinder("base", 0.07, 0.03, (0, 0, 0.015), steel(), btn)
    cylinder("cap", 0.055, 0.03, (0, 0, 0.04), material("g", (46, 158, 91), rough=0.3, coat=0.6), btn)
    text("ok", "approve", 0.028, (0, -0.1, 0.004), ink((236, 238, 244)), top).location.x = 0.42
    return root
