"""Temporal robustness component of fitness."""


def compute_robustness(
    current_priorities: dict[str, float],
    previous_priorities: dict[str, float] | None,
) -> float:
    """Measure stability between cycles. Low change = high robustness.

    Returns a value in [0, 1].
    """
    if previous_priorities is None:
        return 1.0
    common_keys = set(current_priorities.keys()) & set(previous_priorities.keys())
    if not common_keys:
        return 1.0
    deltas = [abs(current_priorities[k] - previous_priorities[k]) for k in common_keys]
    max_delta = max(deltas)
    return max(0.0, 1.0 - max_delta * 2.0)  # Delta of 0.5 -> robustness 0.0
