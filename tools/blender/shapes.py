"""Shared real-object parts for the stage models: wood tiles, brass, steel, glass, LED text, seals, arrows.

These are used by every lesson beyond RAG, so objects that mean the same thing look the same everywhere
(a letter tile is always a wooden tile; a check seal is always a green seal).
"""

import json
import math
import os

import bpy

from blib import box, cylinder, empty, ink, link, material, paper, text
from colors import CARD, GREEN, INK

HERE = os.path.dirname(os.path.abspath(__file__))
MAPLE = (222, 178, 118)
WALNUT = (96, 64, 42)
BRASS = (205, 163, 62)
STEEL_C = (205, 209, 216)
BLACK = (24, 26, 32)
AMBER = (255, 178, 52)
RED = (214, 69, 62)
CREAM = (246, 240, 226)
PALETTE8 = [(47, 111, 214), (46, 158, 91), (224, 154, 27), (138, 92, 209), (26, 159, 163), (212, 80, 74), (214, 69, 138), (110, 120, 135)]


def data(name):
    with open(os.path.join(HERE, "data", f"{name}.json")) as f:
        return json.load(f)


def wood(c=MAPLE):
    return material("wood", c, rough=0.62, coat=0.15)


def brass():
    return material("brass", BRASS, rough=0.28, metal=1.0)


def steel():
    return material("steel", STEEL_C, rough=0.22, metal=1.0)


def glass(c=(190, 215, 240), alpha=0.28):
    m = material("glass", c, rough=0.08, coat=0.5)
    try:
        m.surface_render_method = "BLENDED"
    except (AttributeError, TypeError):
        m.blend_method = "BLEND"
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Alpha"].default_value = alpha
    return m


def led(c=AMBER, strength=4.0):
    return material("led", c, rough=0.4, emit=strength)


def sphere(name, r, loc, mat, parent=None, seg=24):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    if parent is not None:
        o.parent = parent
    return o


def cone(name, r1, r2, depth, loc, mat, parent=None, rot=(0, 0, 0), verts=32):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth, vertices=verts, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    if parent is not None:
        o.parent = parent
    return o


def torus(name, major, minor, loc, mat, parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    if parent is not None:
        o.parent = parent
    return o


def letter_tile(name, ch, parent, loc, size=0.05, color=MAPLE, explode=None, ink_c=INK):
    """A wooden letter tile lying flat. A space is drawn as a paler tile with a dot."""
    g = empty(name, loc, parent, explode)
    pale = ch == " "
    box(f"{name}_b", (size, size, size * 0.28), (0, 0, size * 0.14), wood((236, 214, 170) if pale else color), g, bevel=size * 0.07)
    text(f"{name}_t", "·" if pale else ch, size * 0.7, (0, 0, size * 0.28 + 0.0006), ink(ink_c), g)
    return g


def nameplate(name, label, parent, loc, w=0.2, h=0.05, size=0.026, face=BRASS, ink_c=BLACK, rot=(0, 0, 0)):
    g = empty(name, loc, parent)
    g.rotation_euler = rot
    box(f"{name}_p", (w, h, 0.004), (0, 0, 0), material("plate", face, rough=0.3, metal=0.9 if face == BRASS else 0.0), g, bevel=0.003)
    text(f"{name}_t", label, size, (0, 0, 0.0028), ink(ink_c), g)
    return g


def check_seal(name, parent, loc, r=0.07, ok=True):
    """A round seal with a tick (green) or a cross (red)."""
    g = empty(name, loc, parent)
    col = GREEN if ok else RED
    cylinder(f"{name}_disc", r, 0.012, (0, 0, 0.006), material("seal", col, rough=0.35, coat=0.5), g, verts=40)
    mark = material("mark", (255, 255, 255), rough=0.4)
    if ok:
        for nm, (x1, y1), (x2, y2) in (("a", (-0.38, 0.0), (-0.1, -0.3)), ("b", (-0.1, -0.3), (0.42, 0.36))):
            ln = math.hypot((x2 - x1) * r, (y2 - y1) * r)
            m = box(f"{name}_{nm}", (ln + r * 0.1, r * 0.2, 0.004), ((x1 + x2) / 2 * r, (y1 + y2) / 2 * r, 0.014), mark, g, bevel=0.001)
            m.rotation_euler = (0, 0, math.atan2(y2 - y1, x2 - x1))
    else:
        for s, a in ((1, 45), (2, -45)):
            b = box(f"{name}_x{s}", (r * 0.26, r * 1.4, 0.004), (0, 0, 0.014), mark, g)
            b.rotation_euler = (0, 0, math.radians(a))
    return g


def arrow(name, parent, start, end, color=INK, width=0.014):
    """A flat arrow from start to end (x, y) on the board plane, with a triangular head."""
    sx, sy, z = start
    ex, ey = end[0], end[1]
    dx, dy = ex - sx, ey - sy
    ln = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)
    g = empty(name, (sx, sy, z), parent)
    g.rotation_euler = (0, 0, ang)
    mat = ink(color)
    box(f"{name}_shaft", (ln - 0.04, width, 0.004), ((ln - 0.04) / 2, 0, 0), mat, g)
    c = cone(f"{name}_head", width * 1.6, 0.0, 0.05, (ln - 0.02, 0, 0), mat, g, verts=3)
    c.rotation_euler = (0, math.radians(90), 0)
    return g


def led_panel(name, lines, parent, loc, w=0.8, h=0.22, size=0.07, color=AMBER, rot=(0, 0, 0)):
    """A black display with glowing text lines."""
    g = empty(name, loc, parent)
    g.rotation_euler = rot
    box(f"{name}_frame", (w + 0.03, h + 0.03, 0.02), (0, 0, 0.0), material("frame", (60, 64, 74), rough=0.4, metal=0.8), g, bevel=0.008)
    box(f"{name}_glass", (w, h, 0.004), (0, 0, 0.011), material("screen", BLACK, rough=0.25, coat=0.4), g, bevel=0.004)
    n = len(lines)
    for i, ln in enumerate(lines):
        y = (n - 1) / 2 * size * 1.25 - i * size * 1.25
        text(f"{name}_l{i}", ln, size, (0, y, 0.0135), led(color), g)
    return g
