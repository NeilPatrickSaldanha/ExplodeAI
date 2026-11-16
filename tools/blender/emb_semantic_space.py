"""Embeddings stage 8, Semantic space: the 24 library sentences and yours as points in a glass cube (PCA to 3D).

Real PCA coordinates. Spheres are coloured by topic; your sentence is the pink ring. The picture keeps
27% of the real spread, so distances here are hints, not the exact answer.
"""

from blib import box, cylinder, empty, ink, material
from emb_library import TOPIC
from shapes import data, glass, led, nameplate, sphere, torus

S = 0.42  # half-size of the cube


def build():
    d = data("embeddings")
    root = empty("semantic_space")
    cube = empty("cube", (0, 0, S + 0.02), root)
    box("glass", (2 * S, 2 * S, 2 * S), (0, 0, 0), glass((200, 225, 245), 0.12), cube, bevel=0.01)
    for ax in range(3):
        size = [0.004] * 3
        size[ax] = 2 * S
        box(f"axis{ax}", tuple(size), (0, 0, 0), ink((120, 130, 150)), cube)
    pts = [(it["point"], it["category"]) for it in d["library"]]
    for i, (p, cat) in enumerate(pts):
        x, y, z = p
        sphere(f"p{i}", 0.032, (x * S * 0.9, -z * S * 0.9, y * S * 0.9), material("pt", TOPIC[cat], rough=0.25, coat=0.6), cube, 16)
    qx, qy, qz = d["query_point"]
    torus("query", 0.045, 0.01, (qx * S * 0.9, -qz * S * 0.9, qy * S * 0.9), led((255, 80, 150), 3.0), cube, rot=(1.2, 0, 0))
    nameplate("kept", "27% of the spread kept", root, (0, -S - 0.1, 0.012), 0.5, 0.055, 0.032, rot=(1.1, 0, 0))
    return root
