"""Tests for guardrails."""

from anpegt.guardrails.rules import (
    check_fiscal_ceiling,
    check_priority_variation,
    check_embedding_displacement,
    check_global_coherence,
)
from anpegt.guardrails.checker import GuardrailChecker, Violation
from anpegt.schema.plan import GlobalPlan
from anpegt.schema.config import PartyIdeals, GuardrailsConfig


def test_fiscal_ceiling_ok():
    plan = GlobalPlan(
        cycle_id="c1", sector_plan_ids=[], consolidated_proposals=[],
        conflicts_resolved=[], conflicts_unresolved=[],
        global_budget=50e9, summary="Test",
    )
    violations = check_fiscal_ceiling(plan, 100e9)
    assert len(violations) == 0


def test_fiscal_ceiling_exceeded():
    plan = GlobalPlan(
        cycle_id="c1", sector_plan_ids=[], consolidated_proposals=[],
        conflicts_resolved=[], conflicts_unresolved=[],
        global_budget=150e9, summary="Test",
    )
    violations = check_fiscal_ceiling(plan, 100e9)
    assert len(violations) == 1


def test_priority_variation_ok():
    current = {"a": 0.5, "b": 0.5}
    previous = {"a": 0.45, "b": 0.55}
    violations = check_priority_variation(current, previous, max_delta=0.15)
    assert len(violations) == 0


def test_priority_variation_exceeded():
    current = {"a": 0.8, "b": 0.2}
    previous = {"a": 0.5, "b": 0.5}
    violations = check_priority_variation(current, previous, max_delta=0.15)
    assert len(violations) == 2


def test_embedding_displacement_ok():
    violations = check_embedding_displacement(0.1, 0.3)
    assert len(violations) == 0


def test_embedding_displacement_exceeded():
    violations = check_embedding_displacement(0.5, 0.3)
    assert len(violations) == 1


def test_coherence_ok():
    violations = check_global_coherence(0.8, 0.4)
    assert len(violations) == 0


def test_coherence_low():
    violations = check_global_coherence(0.2, 0.4)
    assert len(violations) == 1


def test_checker_has_critical():
    violations = [
        Violation("test1", "warning", "Minor issue"),
        Violation("test2", "critical", "Major issue"),
    ]
    ideals = PartyIdeals(
        name="Test", non_negotiable_principles=[],
        fiscal_ceiling=1e9, ideological_axes={},
    )
    config = GuardrailsConfig(
        max_priority_delta=0.15, max_embedding_displacement=0.3,
        min_global_coherence=0.4, rollback_on_critical=True,
    )
    checker = GuardrailChecker(ideals, config)
    assert checker.has_critical(violations) is True
    assert checker.has_critical([Violation("test", "warning", "Minor")]) is False
