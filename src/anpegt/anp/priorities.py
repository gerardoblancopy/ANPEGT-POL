"""Priority extraction from ANP limit matrices."""

from __future__ import annotations

import numpy as np

from anpegt.anp.network import ANPNetwork
from anpegt.anp.supermatrix import build_supermatrix, compute_limit_matrix
from anpegt.schema.anp import PrioritySnapshot
from anpegt.util.logging import get_logger

logger = get_logger("anp.priorities")


def extract_priorities(
    limit_matrix: np.ndarray,
    node_ids: list[str],
) -> dict[str, float]:
    """Extract normalised priority weights from a converged limit matrix.

    Takes the first column of the limit matrix (all columns should be
    identical once converged) and normalises the vector so it sums to 1.0.

    Parameters
    ----------
    limit_matrix:
        Square limit matrix produced by :func:`compute_limit_matrix`.
    node_ids:
        Ordered list of node IDs corresponding to the matrix rows.

    Returns
    -------
    dict[str, float]
        Mapping of node_id to its priority value (sums to 1.0).
    """
    col = limit_matrix[:, 0].copy()
    total = col.sum()
    if total > 0.0:
        col /= total
    else:
        logger.warning("Limit matrix first column sums to zero; returning uniform priorities")
        col = np.ones_like(col) / len(col)

    return {nid: float(col[i]) for i, nid in enumerate(node_ids)}


def compute_priorities(
    network: ANPNetwork,
    prev_snapshot: PrioritySnapshot | None = None,
    max_priority_delta: float = 1.0,
) -> PrioritySnapshot:
    """End-to-end ANP priority computation.

    Builds the supermatrix, computes the limit matrix, extracts priorities,
    and optionally clamps changes relative to a previous snapshot.

    Parameters
    ----------
    network:
        A loaded :class:`ANPNetwork`.
    prev_snapshot:
        If provided (together with *max_priority_delta* < 1.0), each
        priority change is clamped so it does not exceed *max_priority_delta*
        from the previous value.
    max_priority_delta:
        Maximum allowed absolute change per node when damping is active.
        A value of 1.0 (default) effectively disables clamping.

    Returns
    -------
    PrioritySnapshot
        A new snapshot with ``cycle_id`` set to ``""`` (the caller is
        responsible for filling it in).
    """
    supermatrix = build_supermatrix(network)
    limit_matrix = compute_limit_matrix(supermatrix)
    priorities = extract_priorities(limit_matrix, network.get_node_ids())

    # Clamp deltas if a previous snapshot is available and damping is active
    if prev_snapshot is not None and max_priority_delta < 1.0:
        clamped: dict[str, float] = {}
        for nid, new_val in priorities.items():
            old_val = prev_snapshot.node_priorities.get(nid, new_val)
            delta = new_val - old_val
            if abs(delta) > max_priority_delta:
                delta = max_priority_delta if delta > 0 else -max_priority_delta
            clamped[nid] = old_val + delta
        # Re-normalise after clamping
        total = sum(clamped.values())
        if total > 0.0:
            clamped = {k: v / total for k, v in clamped.items()}
        priorities = clamped
        logger.info("Priorities clamped with max_priority_delta=%.4f", max_priority_delta)

    logger.info("Priorities computed for %d nodes", len(priorities))

    return PrioritySnapshot(
        cycle_id="",
        node_priorities=priorities,
    )
