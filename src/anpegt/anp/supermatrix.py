"""Supermatrix construction and limit-matrix computation for ANP."""

from __future__ import annotations

import numpy as np

from anpegt.anp.network import ANPNetwork
from anpegt.util.logging import get_logger

logger = get_logger("anp.supermatrix")


def build_supermatrix(network: ANPNetwork) -> np.ndarray:
    """Build a column-stochastic supermatrix from an ANP network.

    Cell ``(i, j)`` holds the weight of the edge from node *j* to node *i*
    (column-stochastic orientation: columns represent the *influencing* node).

    Each column is normalised so that it sums to 1.0.  Columns with no
    outgoing edges remain all-zero.

    Parameters
    ----------
    network:
        A loaded :class:`ANPNetwork`.

    Returns
    -------
    np.ndarray
        Square matrix of shape ``(n, n)`` where *n* is the number of nodes.
    """
    node_ids = network.get_node_ids()
    n = len(node_ids)
    idx = {nid: i for i, nid in enumerate(node_ids)}

    W = np.zeros((n, n), dtype=np.float64)

    for edge in network.edges:
        src = idx.get(edge.source_id)
        tgt = idx.get(edge.target_id)
        if src is not None and tgt is not None:
            # Column = source (influencing), row = target (influenced)
            W[tgt, src] = edge.weight

    # Column-normalise
    col_sums = W.sum(axis=0)
    nonzero = col_sums > 0.0
    W[:, nonzero] = W[:, nonzero] / col_sums[nonzero]

    logger.info("Supermatrix built: %d x %d", n, n)
    return W


def compute_limit_matrix(
    supermatrix: np.ndarray,
    max_iterations: int = 1000,
    tolerance: float = 1e-8,
) -> np.ndarray:
    """Raise the supermatrix to successive powers until convergence.

    Convergence is reached when the maximum absolute difference between
    consecutive powers is below *tolerance*.

    Parameters
    ----------
    supermatrix:
        A column-stochastic square matrix.
    max_iterations:
        Upper bound on the number of matrix multiplications.
    tolerance:
        Convergence threshold.

    Returns
    -------
    np.ndarray
        The limit matrix (same shape as *supermatrix*).
    """
    current = supermatrix.copy()

    for iteration in range(1, max_iterations + 1):
        next_power = current @ supermatrix
        diff = np.max(np.abs(next_power - current))

        if diff < tolerance:
            logger.info(
                "Limit matrix converged after %d iterations (diff=%.2e)",
                iteration,
                diff,
            )
            return next_power

        current = next_power

    logger.warning(
        "Limit matrix did NOT converge after %d iterations (diff=%.2e)",
        max_iterations,
        diff,
    )
    return current
