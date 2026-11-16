# Stage models (Blender)

The 3D objects in every lesson's diagram are built by these scripts in Blender, which is free. Nothing here costs money.

```bash
# from the repository root; stages are lesson:stage (a bare name is the RAG lesson)
blender -b --python tools/blender/build.py -- tok:corpus tok:encoder emb:semantic_space att:mix agt:stop --preview
blender -b --python tools/blender/contact.py -- light tok     # one picture of all the previews of a lesson
```

- Lessons: `rag` (stage_*.py), `tok`, `emb`, `att`, `agt` (named `<lesson>_<stage>.py`). Output goes to `frontend/public/models/<lesson>/<stage>.glb`, Draco-compressed.
- The models show the lessons' real data. `fetch_data.py` saves the real default runs into `data/*.json` (run it from `backend/` with `PYTHONPATH=. uv run python ../tools/blender/fetch_data.py`); the model scripts read those files. If a lesson's data changes, run it again and rebuild.
- Each kind of object looks the same everywhere (`shapes.py`): wooden letter tiles, number-tile strips (blue positive, orange negative), brass name plates, glowing text displays, green and red check seals.
- A node with the custom property `explode` moves by that much when the stage opens up in the app (three.js axes: x right, y up, z towards the viewer).
- The app scales each model to the width given in `geometry.size` in the lesson's `lesson.yaml`, and falls back to the old generic shape if a model cannot load. The Draco decoder is served from `frontend/public/draco`, so nothing loads from a CDN.
- Clear-coat is off on purpose (`blib.COAT`): it makes the browser use a heavier material for everything.
