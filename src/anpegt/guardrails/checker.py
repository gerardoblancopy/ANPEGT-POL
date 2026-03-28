"""Guardrail checker that runs all rules."""

from dataclasses import dataclass, field

from anpegt.schema.plan import GlobalPlan
from anpegt.schema.config import PartyIdeals, GuardrailsConfig
from anpegt.guardrails import rules


@dataclass
class Violation:
    rule_name: str
    severity: str  # "warning" | "critical"
    description: str
    recommendation: str = ""


class GuardrailChecker:
    """Runs all guardrail rules against plans and priorities.

    Parameters
    ----------
    ideals:
        Party ideals containing non-negotiable principles and fiscal ceiling.
    guardrails_config:
        Configuration thresholds for guardrail checks.
    """

    def __init__(
        self, ideals: PartyIdeals, guardrails_config: GuardrailsConfig
    ) -> None:
        self.ideals = ideals
        self.config = guardrails_config

    def check_plan(self, plan: GlobalPlan) -> list[Violation]:
        """Run plan-level guardrail checks.

        Parameters
        ----------
        plan:
            The global plan to validate.

        Returns
        -------
        list[Violation]
            List of detected violations.
        """
        violations = []
        # Non-negotiables
        for v in rules.check_non_negotiables(plan, self.ideals):
            violations.append(
                Violation(
                    "non_negotiable",
                    "critical",
                    v,
                    "Review plan against party principles",
                )
            )
        # Fiscal ceiling
        for v in rules.check_fiscal_ceiling(plan, self.ideals.fiscal_ceiling):
            violations.append(
                Violation(
                    "fiscal_ceiling",
                    "critical",
                    v,
                    "Reduce budget allocations",
                )
            )
        return violations

    def check_priorities(
        self,
        current: dict[str, float],
        previous: dict[str, float] | None,
    ) -> list[Violation]:
        """Check if priority changes exceed allowed delta.

        Parameters
        ----------
        current:
            Current priority values.
        previous:
            Previous priority values (None if first cycle).

        Returns
        -------
        list[Violation]
            List of detected violations.
        """
        violations = []
        for v in rules.check_priority_variation(
            current, previous, self.config.max_priority_delta
        ):
            violations.append(
                Violation(
                    "priority_variation",
                    "warning",
                    v,
                    "Consider dampening priority changes",
                )
            )
        return violations

    def check_embeddings(self, displacement: float) -> list[Violation]:
        """Check if embedding displacement exceeds limit.

        Parameters
        ----------
        displacement:
            The measured embedding displacement.

        Returns
        -------
        list[Violation]
            List of detected violations.
        """
        violations = []
        for v in rules.check_embedding_displacement(
            displacement, self.config.max_embedding_displacement
        ):
            violations.append(
                Violation(
                    "embedding_displacement",
                    "warning",
                    v,
                    "Consider increasing inertia",
                )
            )
        return violations

    def check_coherence(self, coherence_score: float) -> list[Violation]:
        """Check if global coherence falls below minimum.

        Parameters
        ----------
        coherence_score:
            The measured coherence score.

        Returns
        -------
        list[Violation]
            List of detected violations.
        """
        violations = []
        for v in rules.check_global_coherence(
            coherence_score, self.config.min_global_coherence
        ):
            violations.append(
                Violation(
                    "global_coherence",
                    "critical",
                    v,
                    "Review cross-sector alignment",
                )
            )
        return violations

    def has_critical(self, violations: list[Violation]) -> bool:
        """Check if any violation is critical.

        Parameters
        ----------
        violations:
            List of violations to check.

        Returns
        -------
        bool
            True if any violation has severity "critical".
        """
        return any(v.severity == "critical" for v in violations)
