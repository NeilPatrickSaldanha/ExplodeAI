"""Agents stage 8, Stop: a stop sign, and a dial that counts steps against the limit.

The loop ends when the model answers, or when the step limit is reached. In the default Return run the agent
answers on step 6; the limit shown is the default 8 (the experiment's own hard cap is 30).
"""

import math

from blib import box, cylinder, empty, ink, material, plastic, text, wedge
from colors import INK
from shapes import RED, brass, check_seal, cone, nameplate, steel


def build():
    root = empty("stop")
    sign = empty("sign", (-0.3, 0, 0.0), root, explode=(-0.04, 0, 0.03))
    cylinder("pole", 0.018, 0.4, (0, 0, 0.2), steel(), sign, verts=16)
    oct_ = cylinder("octagon", 0.17, 0.02, (0, 0, 0.5), plastic((214, 50, 46)), sign, rot=(1.5708, 0.3927, 0), verts=8)
    cylinder("rim", 0.15, 0.022, (0, -0.002, 0.5), plastic((250, 250, 250)), sign, rot=(1.5708, 0.3927, 0), verts=8)
    cylinder("face", 0.14, 0.024, (0, -0.004, 0.5), plastic((214, 50, 46)), sign, rot=(1.5708, 0.3927, 0), verts=8)
    text("s", "STOP", 0.07, (0, -0.0175, 0.5), ink((255, 255, 255)), sign, rot=(1.5708, 0, 0))
    # step dial
    dial = empty("dial", (0.28, 0, 0.0), root, explode=(0.04, 0, 0.03))
    cylinder("case", 0.2, 0.05, (0, 0, 0.25), steel(), dial, rot=(1.5708, 0, 0), verts=48)
    cylinder("face", 0.185, 0.054, (0, -0.002, 0.25), plastic((250, 247, 238)), dial, rot=(1.5708, 0, 0), verts=48)
    for k in range(9):
        a = math.radians(210 - k * 30)  # 0..8 across a 240 degree sweep
        x, z = 0.15 * math.cos(a), 0.15 * math.sin(a)
        t = box(f"t{k}", (0.02, 0.006, 0.03), (x, -0.03, 0.25 + z), ink(INK), dial)
        t.rotation_euler = (0, math.radians(90) - a + math.radians(90), 0)
        text(f"n{k}", str(k), 0.03, (0.115 * math.cos(a), -0.03, 0.25 + 0.115 * math.sin(a)), ink(INK), dial, rot=(1.5708, 0, 0))
    # needle at 6 (the answer on step 6); red marker at the limit 8
    a6 = math.radians(210 - 6 * 30)
    nd = box("needle", (0.15, 0.008, 0.012), (0.075 * math.cos(a6), -0.034, 0.25 + 0.075 * math.sin(a6)), ink((24, 26, 32)), dial)
    nd.rotation_euler = (0, -a6, 0)
    cylinder("hub", 0.014, 0.012, (0, -0.035, 0.25), ink(INK), dial, rot=(1.5708, 0, 0))
    a8 = math.radians(210 - 8 * 30)
    lim = box("limit", (0.05, 0.01, 0.014), (0.175 * math.cos(a8), -0.034, 0.25 + 0.175 * math.sin(a8)), ink((214, 50, 46)), dial)
    lim.rotation_euler = (0, -a8, 0)
    top = wedge("slope", 0.8, 0.2, 28, root)
    top.location = (0.0, -0.32, 0.0)
    nameplate("a", "answered at step 6", top, (-0.15, 0.0, 0.004), 0.46, 0.05, 0.03, face=(46, 158, 91), ink_c=(255, 255, 255))
    nameplate("b", "limit: 8 steps", top, (0.3, 0.0, 0.004), 0.3, 0.05, 0.03, face=(214, 50, 46), ink_c=(255, 255, 255))
    return root
