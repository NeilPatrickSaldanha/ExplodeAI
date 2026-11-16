"""Stage 7, Page builder: the kept chunks, in rank order, then the question, on one page (the prompt).

The gauge on the right is the room on the page: the three chunks use 66 of the 200 words allowed.
"""

import math

import bpy

from blib import box, empty, ink, link, material, paper, text, text_lines, wedge
from cards import card
from colors import CARD, GREEN, GREY, INK, QUERY

PW, PD = 0.46, 0.6


def clip(name, parent, loc):
    """A steel paper clip, drawn as a bevelled wire curve."""
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.0014
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    pts = [(0, -0.03), (0, 0.022), (0.012, 0.03), (0.024, 0.022), (0.024, -0.024), (0.016, -0.03), (0.008, -0.024), (0.008, 0.012)]
    spline.points.add(len(pts) - 1)
    for p, (x, y) in zip(spline.points, pts):
        p.co = (x, y, 0, 1)
    o = bpy.data.objects.new(name, curve)
    o.data.materials.append(material("steel", (205, 209, 216), rough=0.22, metal=1.0))
    link(o, parent)
    o.location = loc
    return o


def build():
    root = empty("page_builder")
    slope = empty("slope_holder", (-0.06, 0, 0), root)
    page = wedge("slope", PW + 0.04, PD + 0.04, 40, slope)
    box("sheet", (PW, PD, 0.003), (0, 0, 0), paper(CARD), page, bevel=0.0006)
    text("instr_label", "Instructions", 0.026, (-PW / 2 + 0.03, PD / 2 - 0.035, 0.002), ink(INK), page, align="LEFT")
    text_lines("instr", (-PW / 2 + 0.03, PD / 2 - 0.06), [0.36, 0.3], 0.017, 0.005, ink(GREY), page, z=0.0019)
    for i, chunk_id in enumerate(["returns#0", "battery#1", "returns#1"]):
        y = PD / 2 - 0.15 - i * 0.135
        holder = empty(f"slot_{chunk_id}", (0, y, 0.003), page, explode=(0, 0.06 + i * 0.015, 0.02))
        card(chunk_id, holder, (0, 0, 0.0), tilt=0, w=PW - 0.06, h=0.115)
        clip(f"clip_{chunk_id}", holder, (PW / 2 - 0.07, 0.05, 0.004))
    qy = -PD / 2 + 0.065
    text("q_text2", "have to return a bike?", 0.024, (-PW / 2 + 0.045, qy - 0.03, 0.003), ink(INK), page, align="LEFT")
    box("q_box", (PW - 0.06, 0.08, 0.002), (0, qy - 0.015, 0.0015), material("qbox", (252, 229, 239), rough=0.8), page)
    box("q_edge", (0.006, 0.08, 0.003), (-PW / 2 + 0.033, qy - 0.015, 0.002), ink(QUERY), page)
    text("q_text", "Question: How long do I", 0.024, (-PW / 2 + 0.045, qy, 0.003), ink(INK), page, align="LEFT")

    # The budget gauge: 66 of the 200 words allowed are used.
    gauge = empty("gauge", (PW / 2 + 0.04, 0.12, 0.0), root)
    tube_h, used = 0.24, 66 / 200
    box("backboard", (0.08, 0.012, tube_h + 0.02), (0, 0.006, tube_h / 2 + 0.01), paper(CARD), gauge, bevel=0.004)
    box("track", (0.03, 0.004, tube_h), (0, -0.002, tube_h / 2 + 0.01), material("track", (214, 219, 226), rough=0.5), gauge, bevel=0.002)
    box("fill", (0.03, 0.006, tube_h * used), (0, -0.004, tube_h * used / 2 + 0.01), material("fill", GREEN, rough=0.3, coat=0.4), gauge, bevel=0.002)
    for k in range(5):
        z = 0.01 + tube_h * k / 4
        box(f"tick{k}", (0.012, 0.003, 0.002), (0.028, -0.002, z), ink(GREY), gauge)
        text(f"tick{k}_t", str(k * 50), 0.02, (0.042, -0.003, z), ink(INK), gauge, rot=(math.radians(90), 0, 0), align="LEFT")
    tag = empty("gauge_tag", (0, -0.01, tube_h + 0.05), gauge)
    tag.rotation_euler = (math.radians(80), 0, 0)
    box("tag_plate", (0.2, 0.075, 0.003), (0, 0, 0), paper(CARD), tag, bevel=0.002)
    text("tag_text1", "66 / 200", 0.032, (0, 0.012, 0.002), ink(INK), tag)
    text("tag_text2", "words used", 0.02, (0, -0.02, 0.002), ink(GREY), tag)
    return root
