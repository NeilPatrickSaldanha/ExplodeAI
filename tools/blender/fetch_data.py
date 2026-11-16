"""Save the real default-run results the models are drawn from: uv run python ../tools/blender/fetch_data.py (from backend/).

The Blender scripts read these files, so they never need the backend running and always show real numbers.
"""

import json
import pathlib

from app.experiments.agent.pipeline import AgentParams
from app.experiments.agent.pipeline import run as run_agent
from app.experiments.attend.pipeline import AttendParams
from app.experiments.attend.pipeline import run as run_attend
from app.experiments.embed.pipeline import EmbedParams
from app.experiments.embed.pipeline import run as run_embed
from app.experiments.tokenize.pipeline import TokenizeParams
from app.experiments.tokenize.pipeline import run as run_tok

OUT = pathlib.Path(__file__).resolve().parent / "data"
OUT.mkdir(exist_ok=True)


def save(name, obj):
    (OUT / f"{name}.json").write_text(json.dumps(obj, default=float, indent=1))


tok = run_tok(TokenizeParams(text="The keeper lit the lantern at dusk.", merges=100))
save("tokenization", {
    "text": tok["params"]["text"],
    "pre_pieces": [p["text"] for p in tok["encoding"]["pieces"]] if isinstance(tok["encoding"]["pieces"][0], dict) else tok["encoding"]["pieces"],
    "tokens": tok["encoding"]["tokens"],
    "merges": tok["training"]["steps"][:12],
    "merges_learned": tok["training"]["merges_learned"],
    "vocab_size": tok["vocabulary"]["size"],
    "base_size": tok["vocabulary"]["base_size"],
    "pre_sample": tok["pre_tokens"]["sample"],
    "corpus_chars": len(tok["corpus"]["text"]) if isinstance(tok["corpus"], dict) and "text" in tok["corpus"] else None,
    "decoding": tok["decoding"],
})
emb = run_embed(EmbedParams(text="a place to put my books", top_k=10))
save("embeddings", {
    "text": emb["params"]["text"],
    "tokens": emb["query"]["tokens"],
    "norm_before": emb["query"]["norm_before"], "norm_after": emb["query"]["norm_after"], "dim": emb["query"]["dim"],
    "pooled_preview": emb["query"]["pooled_preview"], "query_point": emb["query"]["point"],
    "library": emb["library"]["items"],
    "neighbours": emb["neighbours"],
    "explained_variance": emb["projection"]["explained_variance"],
})
att = run_attend(AttendParams(text="the cat sat on the mat", heads=2, scale=True, causal=False, position=True))
masked = run_attend(AttendParams(text="the cat sat on the mat", heads=2, scale=True, causal=True, position=True))
save("attention", {
    "tokens": [t["text"] for t in att["tokens"]],
    "weights_mean": att["weights_mean"],
    "weights_masked": masked["weights_mean"],
    "heads_masked": [{"weights": h.get("weights")} for h in masked["heads"]],
    "heads": [{k: h.get(k) for k in ("weights", "scores", "scores_raw", "q", "k", "v")} for h in att["heads"]],
    "embedding": att["embedding"],
    "stats": att["stats"],
    "output_preview": att["output"]["preview"],
})
ag = run_agent(AgentParams())
save("agents", {
    "goal": ag["params"]["goal"],
    "tools": [{"name": t["name"], "description": t["description"], "side_effects": t.get("side_effects")} for t in ag["tools"]],
    "steps": [{"index": s["index"], "tokens_in": s["tokens_in"], "kind": s["decision"]["kind"], "tool": s["decision"].get("tool"),
               "arguments": s["decision"].get("arguments"), "scores": s["decision"].get("scores"),
               "validation": s["validation"], "execution": s["execution"]} for s in ag["steps"]],
    "status": ag["status"], "held": ag["held"], "stats": ag["stats"],
})
print("saved", sorted(p.name for p in OUT.iterdir()))
