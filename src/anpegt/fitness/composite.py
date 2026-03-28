"""Composite fitness function combining all components."""
from anpegt.schema.config import FitnessWeightsConfig
from anpegt.schema.fitness import FitnessScore


def compute_composite_fitness(
    cycle_id: str,
    segment_id: str,
    alignment: float,
    coherence: float,
    viability: float,
    robustness: float,
    engagement: float,
    weights: FitnessWeightsConfig,
) -> FitnessScore:
    """Compute composite fitness: F = alpha*A + beta*C + gamma*V + delta*R + epsilon*E."""
    composite = (
        weights.alpha * alignment
        + weights.beta * coherence
        + weights.gamma * viability
        + weights.delta * robustness
        + weights.epsilon * engagement
    )
    return FitnessScore(
        cycle_id=cycle_id,
        segment_id=segment_id,
        alignment=alignment,
        coherence=coherence,
        viability=viability,
        robustness=robustness,
        engagement=engagement,
        composite=composite,
    )
