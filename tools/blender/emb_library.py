"""Embeddings stage 1, Sample library: 24 sentences in four topic crates, six to a crate.

Each sentence is a plastic tag standing in its topic's crate. The topics (animals, food, furniture, vehicles)
keep their colour through the whole lesson, including the dots on the map.
"""

from blib import box, empty, ink, material, plastic, text, wedge
from colors import INK
from shapes import data, nameplate

TOPIC = {"animals": (46, 158, 91), "food": (224, 154, 27), "furniture": (47, 111, 214), "vehicles": (212, 80, 74)}


def build():
    d = data("embeddings")
    root = empty("sample_library")
    top = wedge("slope", 1.2, 0.78, 30, root)
    by = {}
    for it in d["library"]:
        by.setdefault(it["category"], []).append(it)
    for n, (topic, items) in enumerate(by.items()):
        cx = (n % 2 - 0.5) * 0.58
        cy = (0.5 - n // 2) * 0.36
        g = empty(f"crate_{topic}", (cx, cy, 0.003), top, explode=((n % 2 - 0.5) * 0.06, 0.0, (1 - n // 2) * 0.04))
        col = TOPIC[topic]
        w, dd, h = 0.5, 0.28, 0.07
        box("floor", (w, dd, 0.012), (0, 0, 0.006), plastic(col), g, bevel=0.006)
        box("back", (w, 0.012, h), (0, dd / 2, h / 2), plastic(col), g, bevel=0.004)
        box("front", (w, 0.012, h * 0.55), (0, -dd / 2, h * 0.275), plastic(col), g, bevel=0.004)
        for s in (-1, 1):
            box(f"side{s}", (0.012, dd, h), (s * w / 2, 0, h / 2), plastic(col), g, bevel=0.004)
        for i, it in enumerate(items):
            x = (i - 2.5) * 0.077
            tag = empty(f"tag{i}", (x, 0.0, 0.03), g, explode=(0, 0.04, 0.05 + 0.01 * i))
            tag.rotation_euler = (-0.25, 0, 0)
            box("t", (0.07, 0.006, 0.15), (0, 0, 0.075), material("tagc", (250, 247, 238), rough=0.4, coat=0.3), tag, bevel=0.002)
            box("s", (0.07, 0.007, 0.03), (0, -0.001, 0.14), plastic(col), tag)
            words = it["text"].split()
            text("w", " ".join(words[:2]), 0.018, (0, -0.005, 0.09), ink(INK), tag, rot=(1.5708, 0, 0))
        nameplate("topic", topic, g, (0, -dd / 2 - 0.045, 0.012), 0.26, 0.06, 0.04, face=col, ink_c=(255, 255, 255), rot=(-0.55, 0, 0))
    return root
