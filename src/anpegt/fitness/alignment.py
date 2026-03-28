"""Semantic alignment component of fitness."""
import numpy as np


def compute_alignment(
    plan_embedding: np.ndarray, segment_embedding: np.ndarray
) -> float:
    """Cosine similarity between plan/communication embedding and segment embedding.

    Returns a value in [0, 1].
    """
    dot = np.dot(plan_embedding, segment_embedding)
    norms = np.linalg.norm(plan_embedding) * np.linalg.norm(segment_embedding)
    if norms == 0:
        return 0.0
    sim = float(dot / norms)
    return max(0.0, min(1.0, (sim + 1) / 2))  # Map [-1,1] to [0,1]
