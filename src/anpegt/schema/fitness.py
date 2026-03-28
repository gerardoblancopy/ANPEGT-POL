"""Fitness scoring models for ANPEGT-POL."""

from pydantic import Field

from .base import VersionedModel


class FitnessScore(VersionedModel):
    """Multi-objective fitness score for a plan-segment pair."""

    cycle_id: str
    segment_id: str
    alignment: float
    coherence: float
    viability: float
    robustness: float
    engagement: float = Field(default=0.0)
    composite: float
