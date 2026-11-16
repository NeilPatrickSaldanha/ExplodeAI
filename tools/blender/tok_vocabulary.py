"""Tokenization stage 5, Vocabulary: the catalogue of every token with its id, as a cabinet of drawers.

Drawers 256 to 267 hold the first twelve merges; 269 is " keeper" and 275 is " lantern" (gold), the words
the lesson follows. The cabinet stands for 357 entries: 256 bytes + 100 merges + 1 special token.
"""

from blib import box, empty, ink, material, text
from colors import INK
from shapes import BRASS, MAPLE, WALNUT, brass, data, nameplate, wood

COLS, ROWS = 6, 3
DW, DH = 0.18, 0.12


def build():
    d = data("tokenization")
    root = empty("vocabulary")
    merges = {m["token_id"]: m["token"] for m in d["merges"]}
    for t in d["tokens"]:
        merges.setdefault(t["id"], t["text"])
    cells = [(i, merges[i]) for i in sorted(merges) if i >= 256][:COLS * ROWS - 4]
    cells = [(256 + k, merges.get(256 + k)) for k in range(12)] + [(269, merges[269]), (275, merges[275])]
    cells += [(None, "…")] * (COLS * ROWS - len(cells))
    W, H = COLS * DW + 0.05, ROWS * DH + 0.05
    box("carcass", (W, 0.22, H), (0, 0, H / 2 + 0.01), wood(WALNUT), root, bevel=0.008)
    for idx, (tid, tok) in enumerate(cells):
        r, c = divmod(idx, COLS)
        x = (c - (COLS - 1) / 2) * DW
        z = H - 0.045 - r * DH
        gold = tid in (269, 275)
        drawer = empty(f"d{idx}", (x, -0.115, z + 0.01), root, explode=(0, -0.05 - 0.02 * r, 0))
        box(f"d{idx}_face", (DW - 0.014, 0.012, DH - 0.014), (0, 0, 0), wood((236, 200, 130) if gold else MAPLE), drawer, bevel=0.004)
        box(f"d{idx}_knob", (0.03, 0.014, 0.012), (0, -0.012, -DH / 2 + 0.03), brass(), drawer, bevel=0.003)
        rot = (1.5708, 0, 0)
        if tid is not None:
            text(f"d{idx}_id", str(tid), 0.036, (0, -0.0075, 0.025), ink(INK), drawer, rot=rot)
            text(f"d{idx}_tok", tok.replace(" ", "·"), 0.028, (0, -0.0075, -0.012), ink((70, 50, 30)), drawer, rot=rot)
        else:
            text(f"d{idx}_dots", "…", 0.06, (0, -0.0075, 0.0), ink(INK), drawer, rot=rot)
    plate = nameplate("count", "357 entries", root, (0, -0.125, H + 0.045), 0.3, 0.05, 0.034, rot=(1.5708, 0, 0))
    return root
