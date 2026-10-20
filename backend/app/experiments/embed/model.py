"""bge-small-en-v1.5, opened up into its stages.

fastembed normally hides the steps: it tokenizes, runs the transformer, takes the
[CLS] vector and L2-normalizes it. Here each step is separate, so the lesson can
show the real intermediate values. `tests/test_embed.py` checks that doing the
steps by hand reproduces fastembed's own output.

The model files are Qdrant's ONNX export used by fastembed
(Qdrant/bge-small-en-v1.5-onnx-Q). Its model card says "Quantized ONNX port";
its config suggests an fp16, graph-optimized export. Results here are for this
build, which has not been measured against BAAI's original weights. Downloaded
once on first use and cached locally. Requires the optional extra: `uv sync --extra neural`.
"""

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

import numpy as np

MODEL_NAME = "BAAI/bge-small-en-v1.5"
MODEL_BUILD = "Qdrant/bge-small-en-v1.5-onnx-Q (Qdrant's ONNX export, via fastembed)"
MAX_TOKENS = 512
# BGE's documented instruction for short queries in retrieval.
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "

Pooling = Literal["cls", "mean"]


class NeuralUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class Encoded:
    tokens: list[list[str]]
    ids: list[list[int]]
    hidden: list[np.ndarray]  # one (n_tokens, 384) array per text
    truncated: list[bool]


class BgeEncoder:
    def __init__(self) -> None:
        try:
            import onnxruntime as ort
            from fastembed import TextEmbedding
        except ImportError as exc:  # pragma: no cover - depends on the optional extra
            raise NeuralUnavailable("the embeddings lesson needs: uv sync --extra neural") from exc
        self._fastembed = TextEmbedding(MODEL_NAME)
        inner = self._fastembed.model
        model_dir = str(inner._model_dir)
        onnx = next(f for f in os.listdir(model_dir) if f.endswith(".onnx"))
        self._session = ort.InferenceSession(
            os.path.join(model_dir, onnx), providers=["CPUExecutionProvider"]
        )
        self._input_names = {i.name for i in self._session.get_inputs()}
        self.tokenizer = inner.tokenizer
        self.dim = int(self._session.get_outputs()[0].shape[-1])

    def encode(self, texts: list[str]) -> Encoded:
        """Tokenize and run the transformer. Returns per-token vectors (no pooling)."""
        tokens, ids, hidden, truncated = [], [], [], []
        for text in texts:
            enc = self.tokenizer.encode(text)
            # fastembed's tokenizer truncates to the model limit itself (keeping [SEP]
            # last); anything cut off is recorded in `overflowing`.
            was_cut = bool(enc.overflowing) or len(enc.ids) > MAX_TOKENS
            enc_ids = enc.ids[:MAX_TOKENS]
            feeds = {
                "input_ids": np.array([enc_ids], dtype=np.int64),
                "attention_mask": np.ones((1, len(enc_ids)), dtype=np.int64),
            }
            if "token_type_ids" in self._input_names:
                feeds["token_type_ids"] = np.zeros((1, len(enc_ids)), dtype=np.int64)
            out = self._session.run(None, feeds)[0][0]
            tokens.append([self.tokenizer.id_to_token(i) for i in enc_ids])
            ids.append(list(enc_ids))
            hidden.append(out.astype(np.float64))
            truncated.append(was_cut)
        return Encoded(tokens, ids, hidden, truncated)

    def reference(self, texts: list[str]) -> np.ndarray:
        """fastembed's own end-to-end output, for checking the hand-built stages."""
        return np.array(list(self._fastembed.embed(texts)), dtype=np.float64)


def pool(hidden: np.ndarray, mode: Pooling) -> np.ndarray:
    """One vector per text: the [CLS] (first) token's vector, or the mean of all tokens."""
    return hidden[0].copy() if mode == "cls" else hidden.mean(axis=0)


def l2_normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n == 0, 1.0, n)


@lru_cache(maxsize=1)
def get_encoder() -> BgeEncoder:
    return BgeEncoder()


def neural_ready() -> bool:
    try:
        import fastembed  # noqa: F401
        import onnxruntime  # noqa: F401
    except ImportError:
        return False
    return True
