"""Project high-dimensional embeddings to 3D for the vector-space view.

Principal component analysis via SVD on mean-centred chunk vectors. The query
is projected with the same basis. Distances in 3D only approximate distances
in the original space; `explained_variance` says how much of the spread the
three axes keep, and the UI shows it next to the plot.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Projection:
    chunk_points: list[list[float]]
    query_point: list[float]
    explained_variance: float


def pca_3d(chunk_vecs: np.ndarray, query_vec: np.ndarray) -> Projection:
    mean = chunk_vecs.mean(axis=0)
    centred = chunk_vecs - mean
    _, s, vt = np.linalg.svd(centred, full_matrices=False)
    k = min(3, vt.shape[0])
    basis = vt[:k]
    pts = centred @ basis.T
    q = (query_vec - mean) @ basis.T
    if k < 3:  # pad when there are fewer than 3 chunks
        pts = np.pad(pts, ((0, 0), (0, 3 - k)))
        q = np.pad(q, (0, 3 - k))
    scale = float(np.abs(np.vstack([pts, q])).max()) or 1.0
    total = float((s**2).sum()) or 1.0
    return Projection(
        chunk_points=(pts / scale).round(4).tolist(),
        query_point=(q / scale).round(4).tolist(),
        explained_variance=round(float((s[:k] ** 2).sum()) / total, 4),
    )
