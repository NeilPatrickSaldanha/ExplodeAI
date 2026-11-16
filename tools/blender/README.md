# Stage models (Blender)

The 3D objects in the RAG lesson are built by these scripts in Blender, which is free. Nothing here costs money or downloads anything.

```bash
blender -b --python tools/blender/build.py -- corpus chunker embedder vector_index query_encoder question retriever prompt_builder generator --preview
```

- Each `stage_<id>.py` builds one stage. They show the lesson's real data: the six article titles, the 11 chunk ids with their word counts, the real ranking scores, the 66 of 200 words, and the two quoted answer sentences. If the lesson's data changes, update the numbers here and rebuild.
- The colours (one per help article, pink for the question) are in `colors.py` and stay the same in both themes.
- A node with the custom property `explode` moves by that much when the stage opens up in the app (three.js axes: x right, y up, z towards the viewer).
- `blib.optimise()` merges pieces that share a material so the browser draws few objects.
- The app scales each model to the width given in `geometry.size` in the lesson's `lesson.yaml`, and falls back to the old generic shape if a model cannot load.
