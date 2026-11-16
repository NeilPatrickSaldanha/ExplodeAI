"""Build RAG stage models (free, offline): blender -b --python tools/blender/build.py -- <stage> [<stage> ...] [--preview]

Writes frontend/public/models/rag/<stage>.glb. With --preview, also renders dark and light previews to
tools/blender/previews/ (not committed) so a change can be checked before it reaches the site.
"""

import importlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # so the stage modules import

import blib  # noqa: E402
import bpy  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "frontend", "public", "models", "rag")
PREVIEW = os.path.join(HERE, "previews")

args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
preview = "--preview" in args
stages = [a for a in args if not a.startswith("--")]
sizes = {}
for stage in stages:
    blib.reset()
    mod = importlib.import_module(f"stage_{stage}")
    mod.build()
    blib.settle()
    blib.optimise()
    sizes[stage] = blib.export(os.path.join(OUT, f"{stage}.glb"))
    print("OBJECTS", stage, sum(1 for o in bpy.context.scene.objects if o.type == "MESH"), "MATERIALS", len(bpy.data.materials))
    if preview:
        os.makedirs(PREVIEW, exist_ok=True)
        target = getattr(mod, "PREVIEW_TARGET", (0, 0, 0.1))
        dist = getattr(mod, "PREVIEW_DIST", 1.6)
        blib.render_preview(os.path.join(PREVIEW, f"{stage}_dark.png"), (16, 20, 38), target, dist)
        blib.render_preview(os.path.join(PREVIEW, f"{stage}_light.png"), (246, 240, 226), target, dist)
print("SIZES", json.dumps(sizes))
