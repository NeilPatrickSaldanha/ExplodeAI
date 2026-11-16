"""Tile the preview renders into one contact sheet: blender -b --python tools/blender/contact.py -- dark|light"""

import os
import sys

import bpy
import numpy as np

args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
theme = args[0] if args else "dark"
lesson = args[1] if len(args) > 1 else "rag"
here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "previews")
NAMES = {
    "rag": ["corpus", "chunker", "embedder", "vector_index", "query_encoder", "question", "retriever", "prompt_builder", "generator"],
    "tok": ["corpus", "pre_tokenizer", "base_alphabet", "merge_learner", "vocabulary", "input_text", "encoder", "decoder"],
    "emb": ["library", "your_text", "tokenizer", "encoder", "pooling", "normalizer", "similarity", "semantic_space"],
    "att": ["tokens", "embed_pos", "qkv", "scores", "mask", "softmax", "mix", "output"],
    "agt": ["goal", "tools", "decide", "validate", "execute", "observe", "context", "stop"],
}
names = NAMES[lesson]
tiles = []
for n in names:
    img = bpy.data.images.load(os.path.join(here, f"{n}_{theme}.png" if lesson == "rag" else f"{lesson}_{n}_{theme}.png"))
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[::2, ::2]
    tiles.append(px)
th, tw = tiles[0].shape[:2]
rows = (len(tiles) + 2) // 3
sheet = np.zeros((th * rows, tw * 3, 4), dtype=np.float32)
for i, t in enumerate(tiles):
    r, c = divmod(i, 3)
    sheet[(rows - 1 - r) * th:(rows - r) * th, c * tw:(c + 1) * tw] = t  # Blender images start at the bottom row
out = bpy.data.images.new("sheet", tw * 3, th * rows, alpha=True)
out.pixels = sheet.ravel()
out.filepath_raw = os.path.join(here, f"sheet_{lesson}_{theme}.png")
out.file_format = "PNG"
out.save()
