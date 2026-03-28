"""Tests for fitness computation."""

import numpy as np

from anpegt.fitness.alignment import compute_alignment
from anpegt.fitness.coherence import compute_coherence
from anpegt.fitness.viability import compute_viability
from anpegt.fitness.robustness import compute_robustness
from anpegt.fitness.composite import compute_composite_fitness
from anpegt.schema.config import FitnessWeightsConfig


def test_alignment_identical():
    v = np.array([1.0, 0.0, 0.0])
    assert compute_alignment(v, v) == 1.0


def test_alignment_orthogonal():
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([0.0, 1.0, 0.0])
    result = compute_alignment(v1, v2)
    assert abs(result - 0.5) < 0.01  # Mapped to [0,1]


def test_coherence_identical_plans():
    embed_fn = lambda t: [1.0, 0.0, 0.0]
    result = compute_coherence(["plan A", "plan B"], embed_fn)
    assert result == 1.0


def test_coherence_single_plan():
    embed_fn = lambda t: [1.0, 0.0, 0.0]
    assert compute_coherence(["plan A"], embed_fn) == 1.0


def test_viability_under_ceiling():
    assert compute_viability(50e9, 100e9) > 0.5


def test_viability_over_ceiling():
    result = compute_viability(200e9, 100e9)
    assert result < 0.5


def test_viability_zero_budget():
    assert compute_viability(0, 100e9) > 0.9


def test_robustness_no_previous():
    assert compute_robustness({"a": 0.5}, None) == 1.0


def test_robustness_stable():
    current = {"a": 0.5, "b": 0.5}
    previous = {"a": 0.5, "b": 0.5}
    assert compute_robustness(current, previous) == 1.0


def test_robustness_changed():
    current = {"a": 0.7, "b": 0.3}
    previous = {"a": 0.5, "b": 0.5}
    result = compute_robustness(current, previous)
    assert result < 1.0


def test_composite_fitness():
    weights = FitnessWeightsConfig(alpha=0.3, beta=0.2, gamma=0.2, delta=0.15, epsilon=0.15)
    score = compute_composite_fitness(
        cycle_id="c1", segment_id="s1",
        alignment=0.8, coherence=0.7, viability=0.9, robustness=0.95, engagement=0.5,
        weights=weights,
    )
    expected = 0.3*0.8 + 0.2*0.7 + 0.2*0.9 + 0.15*0.95 + 0.15*0.5
    assert abs(score.composite - expected) < 1e-6
