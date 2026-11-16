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
MODELS = os.path.join(HERE, "..", "..", "frontend", "public", "models")
PREVIEW = os.path.join(HERE, "previews")

args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
preview = "--preview" in args
stages = [a for a in args if not a.startswith("--")]
sizes = {}
# "tok:corpus" builds models/tok/corpus.glb from stage module tok_corpus; a bare "corpus" is the RAG lesson.
for spec in stages:
    lesson, _, stage = spec.rpartition(":")
    lesson = lesson or "rag"
    blib.reset()
    mod = importlib.import_module(f"stage_{stage}" if lesson == "rag" else f"{lesson}_{stage}")
    OUT = os.path.join(MODELS, lesson)
    mod.build()
    blib.stand()
    blib.settle()
    blib.optimise()
    sizes[spec] = blib.export(os.path.join(OUT, f"{stage}.glb"))
    tris = sum(len(o.data.polygons) for o in bpy.context.scene.objects if o.type == "MESH")
    print("TRIS", spec, tris)
    print("OBJECTS", spec, sum(1 for o in bpy.context.scene.objects if o.type == "MESH"), "MATERIALS", len(bpy.data.materials))
    if preview:
        os.makedirs(PREVIEW, exist_ok=True)
        (x0, x1), (y0, y1), (z0, z1) = blib.bounds(list(bpy.context.scene.objects))
        target = (0, 0, (z1 - z0) * 0.45)
        dist = 1.25 * max(x1 - x0, y1 - y0, z1 - z0) + 0.7
        blib.render_preview(os.path.join(PREVIEW, f"{lesson}_{stage}_dark.png"), (16, 20, 38), target, dist)
        blib.render_preview(os.path.join(PREVIEW, f"{lesson}_{stage}_light.png"), (246, 240, 226), target, dist)
print("SIZES", json.dumps(sizes))
