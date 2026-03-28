"""Cross-sector coherence component of fitness."""
from typing import Callable

import numpy as np


def compute_coherence(
    sector_plan_texts: list[str], embed_fn: Callable[[str], list[float]]
) -> float:
    """Compute pairwise cosine similarity of sector plan embeddings.

    Returns mean similarity in [0, 1].
    """
    if len(sector_plan_texts) < 2:
        return 1.0
    embeddings = [np.array(embed_fn(t)) for t in sector_plan_texts]
    similarities = []
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            dot = np.dot(embeddings[i], embeddings[j])
            norms = np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
            sim = float(dot / norms) if norms > 0 else 0.0
            similarities.append((sim + 1) / 2)  # Map to [0, 1]
    return float(np.mean(similarities))
