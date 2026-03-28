"""Tests for the ANP engine."""

import numpy as np
import yaml

from anpegt.anp.network import ANPNetwork, load_anp_network
from anpegt.anp.supermatrix import build_supermatrix, compute_limit_matrix
from anpegt.anp.priorities import extract_priorities, compute_priorities


def test_load_network_from_yaml(config_dir):
    with open(f"{config_dir}/anp_network.yaml") as f:
        net_def = yaml.safe_load(f)
    network = load_anp_network(net_def)
    assert len(network.nodes) == 9
    assert len(network.edges) == 32


def test_supermatrix_shape():
    net_def = {
        "clusters": [{"id": "c1", "name": "C1"}, {"id": "c2", "name": "C2"}],
        "nodes": [
            {"node_id": "a", "name": "A", "cluster_id": "c1", "node_type": "criterion"},
            {"node_id": "b", "name": "B", "cluster_id": "c2", "node_type": "alternative"},
        ],
        "edges": [{"source_id": "a", "target_id": "b", "weight": 0.8}],
    }
    network = load_anp_network(net_def)
    sm = build_supermatrix(network)
    assert sm.shape == (2, 2)


def test_limit_matrix_convergence():
    """Test with a known 3x3 matrix that should converge."""
    net_def = {
        "clusters": [{"id": "c", "name": "C"}],
        "nodes": [
            {"node_id": "x", "name": "X", "cluster_id": "c", "node_type": "criterion"},
            {"node_id": "y", "name": "Y", "cluster_id": "c", "node_type": "criterion"},
            {"node_id": "z", "name": "Z", "cluster_id": "c", "node_type": "criterion"},
        ],
        "edges": [
            {"source_id": "x", "target_id": "y", "weight": 0.5},
            {"source_id": "y", "target_id": "z", "weight": 0.7},
            {"source_id": "z", "target_id": "x", "weight": 0.3},
            {"source_id": "x", "target_id": "z", "weight": 0.4},
            {"source_id": "y", "target_id": "x", "weight": 0.6},
            {"source_id": "z", "target_id": "y", "weight": 0.8},
        ],
    }
    network = load_anp_network(net_def)
    sm = build_supermatrix(network)
    limit = compute_limit_matrix(sm)
    # All columns should be identical in a converged matrix
    for col in range(limit.shape[1]):
        np.testing.assert_allclose(limit[:, col], limit[:, 0], atol=1e-6)


def test_priorities_sum_to_one():
    net_def = {
        "clusters": [{"id": "c", "name": "C"}],
        "nodes": [
            {"node_id": "a", "name": "A", "cluster_id": "c", "node_type": "criterion"},
            {"node_id": "b", "name": "B", "cluster_id": "c", "node_type": "criterion"},
        ],
        "edges": [
            {"source_id": "a", "target_id": "b", "weight": 0.6},
            {"source_id": "b", "target_id": "a", "weight": 0.4},
        ],
    }
    network = load_anp_network(net_def)
    snap = compute_priorities(network)
    total = sum(snap.node_priorities.values())
    assert abs(total - 1.0) < 1e-6


def test_compute_priorities_from_real_config(config_dir):
    with open(f"{config_dir}/anp_network.yaml") as f:
        net_def = yaml.safe_load(f)
    network = load_anp_network(net_def)
    snap = compute_priorities(network)
    assert len(snap.node_priorities) == 9
    total = sum(snap.node_priorities.values())
    assert abs(total - 1.0) < 1e-6
    # salud_plan should have highest priority based on our config
    assert snap.node_priorities["salud_plan"] > 0.1
