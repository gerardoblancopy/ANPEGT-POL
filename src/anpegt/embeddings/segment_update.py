"""Voter segment embedding evolutionary update."""
import numpy as np


def update_segment_embedding(
    old_embedding: np.ndarray,
    communication_embedding: np.ndarray,
    inertia: float = 0.7,
    influence_factor: float = 0.25,
    noise_scale: float = 0.05,
    max_displacement: float = 0.3,
) -> tuple[np.ndarray, float]:
    """Update a voter segment embedding based on communication influence.

    Returns (new_embedding, displacement) where displacement is cosine distance from old.
    """
    noise = np.random.normal(0, noise_scale, old_embedding.shape).astype(np.float32)
    new = (1 - inertia) * old_embedding + influence_factor * communication_embedding + noise

    # Normalize
    norm = np.linalg.norm(new)
    if norm > 0:
        new = new / norm

    # Compute displacement (cosine distance = 1 - cosine_similarity)
    cos_sim = np.dot(old_embedding, new) / (
        np.linalg.norm(old_embedding) * np.linalg.norm(new) + 1e-10
    )
    displacement = 1.0 - float(cos_sim)

    # Apply max displacement guardrail: interpolate back if exceeded
    if displacement > max_displacement and max_displacement > 0:
        # Interpolate between old and new to limit displacement
        alpha = max_displacement / (displacement + 1e-10)
        new = (1 - alpha) * old_embedding + alpha * new
        norm = np.linalg.norm(new)
        if norm > 0:
            new = new / norm
        cos_sim = np.dot(old_embedding, new) / (
            np.linalg.norm(old_embedding) * np.linalg.norm(new) + 1e-10
        )
        displacement = 1.0 - float(cos_sim)

    return new, displacement
