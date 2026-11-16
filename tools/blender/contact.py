"""Tile the preview renders into one contact sheet: blender -b --python tools/blender/contact.py -- dark|light"""

import os
import sys

import bpy
import numpy as np

theme = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "dark"
here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "previews")
names = ["corpus", "chunker", "embedder", "vector_index", "query_encoder", "question", "retriever", "prompt_builder", "generator"]
tiles = []
for n in names:
    img = bpy.data.images.load(os.path.join(here, f"{n}_{theme}.png"))
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[::2, ::2]
    tiles.append(px)
th, tw = tiles[0].shape[:2]
sheet = np.zeros((th * 3, tw * 3, 4), dtype=np.float32)
for i, t in enumerate(tiles):
    r, c = divmod(i, 3)
    sheet[(2 - r) * th:(3 - r) * th, c * tw:(c + 1) * tw] = t  # Blender images start at the bottom row
out = bpy.data.images.new("sheet", tw * 3, th * 3, alpha=True)
out.pixels = sheet.ravel()
out.filepath_raw = os.path.join(here, f"sheet_{theme}.png")
out.file_format = "PNG"
out.save()
