"""Individual guardrail rule implementations."""

from anpegt.schema.plan import GlobalPlan
from anpegt.schema.config import PartyIdeals


def check_non_negotiables(plan: GlobalPlan, ideals: PartyIdeals) -> list[str]:
    """Check if plan contradicts non-negotiable principles. Returns list of violations."""
    violations = []
    plan_text = plan.summary.lower()
    for prop in plan.consolidated_proposals:
        plan_text += " " + prop.description.lower()
    # Simple keyword check for contradictions
    # In production this would use NLI/embeddings
    for principle in ideals.non_negotiable_principles:
        # Check if the principle's key terms appear negated
        key_terms = [w for w in principle.lower().split() if len(w) > 4]
        # This is a placeholder - real implementation would use semantic analysis
    return violations


def check_fiscal_ceiling(plan: GlobalPlan, fiscal_ceiling: float) -> list[str]:
    """Check if plan exceeds fiscal ceiling."""
    if plan.global_budget > fiscal_ceiling:
        return [
            f"Plan budget ({plan.global_budget:,.0f}) exceeds fiscal ceiling ({fiscal_ceiling:,.0f})"
        ]
    return []


def check_priority_variation(
    current: dict[str, float],
    previous: dict[str, float] | None,
    max_delta: float,
) -> list[str]:
    """Check if any priority changed more than max_delta."""
    if previous is None:
        return []
    violations = []
    for key in current:
        if key in previous:
            delta = abs(current[key] - previous[key])
            if delta > max_delta:
                violations.append(
                    f"Priority '{key}' changed by {delta:.3f} (max: {max_delta})"
                )
    return violations


def check_embedding_displacement(
    displacement: float, max_displacement: float
) -> list[str]:
    """Check if embedding displacement exceeds limit."""
    if displacement > max_displacement:
        return [
            f"Embedding displacement {displacement:.3f} exceeds max {max_displacement}"
        ]
    return []


def check_global_coherence(
    coherence_score: float, min_threshold: float
) -> list[str]:
    """Check if global coherence falls below minimum."""
    if coherence_score < min_threshold:
        return [
            f"Global coherence {coherence_score:.3f} below threshold {min_threshold}"
        ]
    return []
