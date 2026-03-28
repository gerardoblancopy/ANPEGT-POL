"""Fiscal viability component of fitness."""


def compute_viability(total_budget: float, fiscal_ceiling: float) -> float:
    """Score viability based on budget vs ceiling.

    Returns a value in [0, 1].
    """
    if fiscal_ceiling <= 0:
        return 0.0
    ratio = total_budget / fiscal_ceiling
    if ratio <= 1.0:
        return 1.0 - (ratio * 0.3)  # Some penalty even when under budget (efficiency)
    else:
        return max(0.0, 1.0 - (ratio - 1.0) * 5.0)  # Sharp penalty for exceeding
